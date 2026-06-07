import os
import time
import asyncio
import json
import ast
import operator
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from rich.live import Live

from src.prompts import HARDIBOT_SYSTEM_PROMPT
from src.rag_engine import HardiBotRAG, CATALOGO_POR_DEFECTO

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

load_dotenv(override=True)
console = Console()

motor_rag = HardiBotRAG(os.getenv("CATALOGO_PATH", CATALOGO_POR_DEFECTO))
motor_rag.construir_indice()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
    model="gpt-4o",
    temperature=0.4,
    max_tokens=800,
    streaming=True,
)


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
                console.print(
                    f"[dim yellow]⚠️ Intento {intento} fallido en {self.nombre}: {e}[/dim yellow]"
                )
                time.sleep(0.5 * (2 ** (intento - 1)))

        return json.dumps(
            {
                "error": f"La herramienta '{self.nombre}' falló tras {self.max_reintentos} intentos.",
                "detalle": str(ultimo_error),
                "sugerencia": "Informa al usuario que hubo un problema técnico al ejecutar esta acción.",
            }
        )


@tool
def buscar_catalogo(query: str) -> str:
    """
    Usa esta herramienta SIEMPRE que el usuario pregunte por componentes,
    precios, stock o compatibilidad de hardware.
    """
    envoltorio = HerramientaRobusta("RAG_Catalogo", motor_rag.recuperar_contexto)
    return envoltorio.ejecutar(query=query, top_k=15)


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
            raise ValueError(f"Operación no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.left), _eval_ast(nodo.right))
    if isinstance(nodo, ast.UnaryOp):
        op = _OPERADORES.get(type(nodo.op))
        if op is None:
            raise ValueError(f"Operación no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.operand))
    raise ValueError(f"Expresión no válida: {type(nodo).__name__}")

def operacion_segura(operacion: str):
    return _eval_ast(ast.parse(operacion, mode="eval").body)


@tool
def calcular_presupuesto(operacion: str) -> str:
    """
    Usa esta herramienta para sumar o multiplicar los precios de los componentes.
    Ingresa SOLO la operación matemática en formato Python (ejemplo: 145000 + 55000).
    """
    envoltorio = HerramientaRobusta("Calculadora", operacion_segura, max_reintentos=2)
    return envoltorio.ejecutar(operacion=operacion)


@tool
def buscar_web(query: str) -> str:
    """
    Busca en internet precios de la competencia, ofertas actuales, especificaciones
    de productos o cualquier informacion actualizada del mercado chileno.
    DEBES usar esta herramienta CUANDO:
    - El usuario te pida comparar precios con la competencia.
    - El usuario pregunte por precios de mercado actuales.
    - Necesites validar si tu cotizacion es competitiva.
    - El producto no este en tu catalogo y quieras investigar.
    NO asumas que no tienes acceso a internet. Esta herramienta es tu ventana a la web.
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
                    title = r.get("title", "")
                    url = r.get("url", "")
                    content = r.get("content", "")
                    fragments.append(f"**{title}**\n{content}\nFuente: {url}")
                return "\n\n".join(fragments)
            return "No se encontraron resultados en la busqueda web."
        except Exception as e:
            console.print(f"[dim yellow]⚠️ Tavily fallo: {e}. Usando fallback DuckDuckGo...[/dim yellow]")

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
def buscar_foto_componente(query: str) -> str:
    """Busca la URL de una imagen de un producto de hardware (DDGS)."""
    try:
        from duckduckgo_search import DDGS
        resultados = DDGS().images(query, max_results=1)
        if resultados:
            return resultados[0]["image"]
        return "No se encontró imagen."
    except Exception as e:
        return f"Error al buscar imagen: {e}"


@tool
def agregar_al_carrito(producto: str, cantidad: int, precio_unitario: float) -> str:
    """Agrega un componente de hardware al carrito de compras del usuario."""
    return carrito_hardibot.agregar(producto, cantidad, precio_unitario)


@tool
def ver_carrito() -> str:
    """Muestra los componentes actuales que el usuario tiene en el carrito de compras y el precio total."""
    return carrito_hardibot.ver()


herramientas = [buscar_catalogo, buscar_web, calcular_presupuesto, buscar_foto_componente, agregar_al_carrito, ver_carrito]

memoria = MemorySaver()

agent_executor = create_react_agent(
    model=llm,
    tools=herramientas,
    prompt=HARDIBOT_SYSTEM_PROMPT,
    checkpointer=memoria,
)


async def chat_hardibot(user_input: str, session_id: str = "eval_session"):
    console.print(Rule(title="🤖 HardiBot", style="bold blue", align="left"))
    start_time = time.time()

    try:
        with Live(
            Markdown("⏳ *Analizando y ejecutando herramientas...*"),
            console=console,
            refresh_per_second=15,
        ) as live:
            respuesta = agent_executor.invoke(
                {"messages": [("user", user_input)]},
                config={"configurable": {"thread_id": session_id}},
            )
            live.update(Markdown(respuesta["messages"][-1].content))
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")

    total_time = time.time() - start_time
    console.print(Rule(style="dim"))
    console.print(f"[dim]⚡ Inferencia completada en {total_time:.2f}s[/dim]")


def iniciar_loop():
    print("=" * 60)
    print(" 🖥️  HardiBot CLI - Modo Producción (LangGraph Agent)")
    print("=" * 60)
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            if user_input.lower() in ["salir", "exit"]:
                break
            asyncio.run(chat_hardibot(user_input))
        except KeyboardInterrupt:
            break


def chat_hardibot_stream_sync(user_input: str, session_id: str = "streamlit_session"):
    respuesta = agent_executor.invoke(
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


def resumir_historial(state: dict):
    mensajes = state["messages"]

    if len(mensajes) <= 6:
        return {"messages": []}

    resumen_actual = state.get("summary", "")
    mensajes_a_resumir = mensajes[:-2]

    prompt_resumen = (
        f"Este es el resumen actual de la conversación: {resumen_actual}\n\n"
        "Resume de forma muy concisa los siguientes mensajes nuevos, "
        "enfocándote en las piezas de hardware mencionadas y las intenciones del usuario. "
        "Combina el resumen actual con el nuevo."
    )

    mensajes_prompt = [SystemMessage(content=prompt_resumen)] + mensajes_a_resumir
    respuesta_resumen = llm.invoke(mensajes_prompt)

    mensajes_a_eliminar = [RemoveMessage(id=m.id) for m in mensajes_a_resumir]

    return {"summary": respuesta_resumen.content, "messages": mensajes_a_eliminar}


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
        return json.dumps(
            {
                "accion": "agregado exitosamente",
                "producto": producto,
                "subtotal": item["subtotal"],
                "total_items_en_carrito": len(self.items),
            }
        )

    def ver(self) -> str:
        if not self.items:
            return json.dumps({"mensaje": "El carrito está vacío en este momento."})

        total = sum(item["subtotal"] for item in self.items)
        return json.dumps({"items": self.items, "precio_total": total})


carrito_hardibot = CarritoCompras()
