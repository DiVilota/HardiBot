import os
import time
import asyncio
import json
import ast
import operator
from datetime import datetime, timezone
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from rich.live import Live

from src.rag_engine import HardiBotRAG
from src.personas import PERSONAS, obtener_prompt

from langchain_core.tools import tool
from langchain_core.callbacks import BaseCallbackHandler
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv(override=True)
console = Console()

MODELO_POR_DEFECTO = os.getenv("MODEL_NAME", "gpt-4o")


class ToolCaptureHandler(BaseCallbackHandler):
    """Captura el uso de herramientas del agente para mostrarlo en la UI."""

    def __init__(self):
        self.tool_calls = []
        self._start_times = {}
        self._current_step = 0

    def on_tool_start(self, serialized, input_str, run_id=None, **kwargs):
        name = serialized.get("name", "unknown")
        self._current_step += 1
        self._start_times[run_id] = time.time()
        self.tool_calls.append({
            "step": self._current_step,
            "name": name,
            "input": str(input_str)[:200],
            "output": None,
            "duration": None,
            "status": "running",
        })

    def on_tool_end(self, output, run_id=None, **kwargs):
        for tc in reversed(self.tool_calls):
            if tc["output"] is None:
                tc["output"] = str(output)[:300]
                tc["duration"] = round(time.time() - self._start_times.get(run_id, time.time()), 2)
                tc["status"] = "complete"
                break


def ejecutar_con_visibilidad(user_input: str, session_id: str = "streamlit_session"):
    """Ejecuta el agente y retorna (tool_calls, response_text, metadata)."""
    start = time.time()
    handler = ToolCaptureHandler()

    respuesta = app_state.agent.invoke(
        {"messages": [("user", user_input)]},
        config={
            "configurable": {"thread_id": session_id},
            "callbacks": [handler],
        },
    )

    elapsed = round(time.time() - start, 2)
    mensajes = respuesta["messages"]
    textos_ia = []
    for msg in reversed(mensajes):
        if msg.type == "human":
            break
        if msg.type == "ai" and msg.content:
            textos_ia.insert(0, msg.content)

    metadata = {
        "latencia": elapsed,
        "total_mensajes": len(mensajes),
        "herramientas_usadas": len(handler.tool_calls),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return handler.tool_calls, "\n\n---\n\n".join(textos_ia), metadata


class CarritoCompras:
    def __init__(self):
        self.items = []

    def agregar(self, producto: str, cantidad: int, precio_unitario: float) -> str:
        item = {
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": cantidad * precio_unitario,
        }
        self.items.append(item)
        return json.dumps({
            "accion": "agregado exitosamente",
            "producto": producto,
            "subtotal": item["subtotal"],
            "total_items_en_carrito": len(self.items),
        })

    def ver(self) -> str:
        if not self.items:
            return json.dumps({"mensaje": "El carrito esta vacio en este momento."})
        total = sum(item["subtotal"] for item in self.items)
        return json.dumps({"items": self.items, "precio_total": total})

    def limpiar(self):
        self.items = []


class HerramientaRobusta:
    def __init__(self, nombre: str, funcion, max_reintentos: int = 3):
        self.nombre = nombre
        self.funcion = funcion
        self.max_reintentos = max_reintentos

    def ejecutar(self, **kwargs) -> str:
        ultimo_error = None
        for intento in range(1, self.max_reintentos + 1):
            try:
                resultado = self.funcion(**kwargs)
                return str(resultado)
            except Exception as e:
                ultimo_error = e
                console.print(f"[dim yellow]Intento {intento} fallido en {self.nombre}: {e}[/dim yellow]")
                time.sleep(0.5 * (2 ** (intento - 1)))
        return json.dumps({
            "error": f"La herramienta '{self.nombre}' fallo tras {self.max_reintentos} intentos.",
            "detalle": str(ultimo_error),
            "sugerencia": "Informa al usuario que hubo un problema tecnico al ejecutar esta accion.",
        })


_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_ast(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
        return nodo.value
    if isinstance(nodo, ast.BinOp):
        op = _OPERADORES.get(type(nodo.op))
        if op is None:
            raise ValueError(f"Operacion no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.left), _eval_ast(nodo.right))
    if isinstance(nodo, ast.UnaryOp):
        op = _OPERADORES.get(type(nodo.op))
        if op is None:
            raise ValueError(f"Operacion no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.operand))
    raise ValueError(f"Expresion no valida: {type(nodo).__name__}")

def operacion_segura(operacion: str):
    return _eval_ast(ast.parse(operacion, mode="eval").body)


_TOOLS = []


class HardiBotAppState:
    """Estado mutable de la aplicacion. Se puede reconfigurar en caliente."""

    def __init__(self, persona_id: str = "hardware"):
        self.persona_id = persona_id
        self.config = PERSONAS[persona_id]
        self.motor_rag = HardiBotRAG(self.config["catalogo"])
        self.motor_rag.construir_indice()
        self.prompt = obtener_prompt(persona_id)
        self.llm = ChatOpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("GITHUB_TOKEN"),
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.4")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "800")),
            streaming=True,
        )
        self.carrito = CarritoCompras()
        self.memoria = MemorySaver()
        self.agent = None

    def iniciar(self):
        self.agent = create_react_agent(
            model=self.llm,
            tools=_TOOLS,
            prompt=self.prompt,
            checkpointer=self.memoria,
        )
        return self

    def reconfigurar(self, persona_id: str):
        console.print(f"[bold cyan]--- Cambiando a persona: {persona_id} ---[/bold cyan]")
        self.persona_id = persona_id
        self.config = PERSONAS[persona_id]
        self.motor_rag = HardiBotRAG(self.config["catalogo"])
        self.motor_rag.construir_indice()
        self.prompt = obtener_prompt(persona_id)
        self.carrito.limpiar()
        self.memoria = MemorySaver()
        self.agent = create_react_agent(
            model=self.llm,
            tools=_TOOLS,
            prompt=self.prompt,
            checkpointer=self.memoria,
        )
        console.print(f"[bold green]Persona cambiada a: {self.config['nombre']}[/bold green]")

    @property
    def nombre_bot(self) -> str:
        return self.config["nombre"]

    @property
    def titulo_bot(self) -> str:
        return self.config["titulo"]


@tool
def _buscar_catalogo(query: str) -> str:
    """Usa esta herramienta SIEMPRE que el usuario pregunte por componentes, precios, stock o compatibilidad."""
    env = HerramientaRobusta("RAG_Catalogo", app_state.motor_rag.recuperar_contexto)
    return env.ejecutar(query=query, top_k=15)


@tool
def _buscar_web(query: str) -> str:
    """
    Busca en internet precios de la competencia, ofertas actuales, especificaciones
    de productos o cualquier informacion actualizada del mercado chileno.
    DEBES usar esta herramienta CUANDO:
    - El usuario te pida comparar precios con la competencia.
    - El usuario pregunte por precios de mercado actuales.
    - Necesites validar si tu cotizacion es competitiva.
    - El producto no este en tu catalogo y quieras investigar.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            resultados = client.search(query=query, search_depth="advanced", max_results=5)
            if resultados and "results" in resultados:
                fragments = []
                for r in resultados["results"][:5]:
                    fragments.append(f"**{r.get('title', '')}**\n{r.get('content', '')}\nFuente: {r.get('url', '')}")
                return "\n\n".join(fragments)
            return "No se encontraron resultados en la busqueda web."
        except Exception as e:
            console.print(f"[dim yellow]Tavily fallo: {e}. Usando fallback DuckDuckGo...[/dim yellow]")

    try:
        from duckduckgo_search import DDGS
        resultados = DDGS().text(query, max_results=5)
        fragments = []
        for r in resultados:
            fragments.append(f"**{r.get('title', '')}**\n{r.get('body', '')}\nFuente: {r.get('href', '')}")
        return "\n\n".join(fragments) if fragments else "No se encontraron resultados en la busqueda web."
    except Exception as e:
        return json.dumps({
            "error": "No se pudo realizar la busqueda web.",
            "detalle": str(e),
            "sugerencia": "Informa al usuario que no hay conectividad a internet en este momento.",
        })


@tool
def _calcular_presupuesto(operacion: str) -> str:
    """Usa esta herramienta para sumar o multiplicar los precios de los componentes. Ingresa SOLO la operacion matematica."""
    env = HerramientaRobusta("Calculadora", operacion_segura, max_reintentos=2)
    return env.ejecutar(operacion=operacion)


@tool
def _buscar_foto_componente(query: str) -> str:
    """Busca la URL de una imagen de un producto (DDGS)."""
    try:
        from duckduckgo_search import DDGS
        resultados = DDGS().images(query, max_results=1)
        if resultados:
            return resultados[0]["image"]
        return "No se encontro imagen."
    except Exception as e:
        return f"Error al buscar imagen: {e}"


@tool
def _agregar_al_carrito(producto: str, cantidad: int, precio_unitario: float) -> str:
    """Agrega un producto al carrito de compras del usuario."""
    return app_state.carrito.agregar(producto, cantidad, precio_unitario)


@tool
def _ver_carrito() -> str:
    """Muestra los productos actuales en el carrito de compras y el precio total."""
    return app_state.carrito.ver()


_TOOLS[:] = [_buscar_catalogo, _buscar_web, _calcular_presupuesto, _buscar_foto_componente, _agregar_al_carrito, _ver_carrito]

app_state = HardiBotAppState(os.getenv("PERSONA_ID", "hardware")).iniciar()


def reconfigurar_agente(persona_id: str) -> dict:
    """Cambia la personalidad del bot en caliente. Usado desde la UI."""
    app_state.reconfigurar(persona_id)
    return {"persona_id": persona_id, "nombre": app_state.nombre_bot, "titulo": app_state.titulo_bot}


async def chat_hardibot(user_input: str, session_id: str = "eval_session"):
    console.print(Rule(title=f"HardiBot ({app_state.persona_id})", style="bold blue", align="left"))
    start_time = time.time()
    try:
        with Live(Markdown("Analizando y ejecutando herramientas..."), console=console, refresh_per_second=15) as live:
            respuesta = app_state.agent.invoke(
                {"messages": [("user", user_input)]},
                config={"configurable": {"thread_id": session_id}},
            )
            live.update(Markdown(respuesta["messages"][-1].content))
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
    total_time = time.time() - start_time
    console.print(Rule(style="dim"))
    console.print(f"[dim]Inferencia completada en {total_time:.2f}s[/dim]")


def iniciar_loop():
    print("=" * 60)
    print(f"  {app_state.nombre_bot} CLI - Modo Produccion")
    print("=" * 60)
    while True:
        try:
            user_input = input("\nTu: ").strip()
            if user_input.lower() in ["salir", "exit"]:
                break
            asyncio.run(chat_hardibot(user_input))
        except KeyboardInterrupt:
            break


def chat_hardibot_stream_sync(user_input: str, session_id: str = "streamlit_session"):
    respuesta = app_state.agent.invoke(
        {"messages": [("user", user_input)]},
        config={"configurable": {"thread_id": session_id}},
    )
    mensajes = respuesta["messages"]
    textos_ia = []
    for msg in reversed(mensajes):
        if msg.type == "human":
            break
        if msg.type == "ai" and msg.content:
            textos_ia.insert(0, msg.content)
    texto_final = "\n\n---\n\n".join(textos_ia)
    for palabra in texto_final.split(" "):
        yield palabra + " "
        time.sleep(0.02)


