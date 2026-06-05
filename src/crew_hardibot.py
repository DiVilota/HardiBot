import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Cargar variables y mapear para CrewAI (Requisito crítico de tu rúbrica)
load_dotenv(override=True)
os.environ["OPENAI_API_BASE"] = os.environ.get("OPENAI_BASE_URL", "")
os.environ["OPENAI_API_KEY"] = os.environ.get("GITHUB_TOKEN", "")


# --- PASO 2: ORQUESTACIÓN MULTI-AGENTE (Roles Especializados) ---

ingeniero_hardware = Agent(
    role="Ingeniero de Hardware Senior",
    goal="Validar compatibilidad técnica y viabilidad de presupuesto de los componentes solicitados.",
    backstory="Eres un experto técnico pragmático. Conoces todos los cuellos de botella y precios del mercado chileno.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o",  # Usamos el mismo modelo para ambos agentes para mantener coherencia en el tono y nivel técnico
)

ejecutivo_ventas = Agent(
    role="Ejecutivo de Ventas y Atención al Cliente",
    goal="Redactar cotizaciones atractivas y amigables basadas en los datos técnicos del ingeniero.",
    backstory="Eres el rostro amigable de la tienda. Tu objetivo es que el cliente entienda la propuesta técnica y quiera comprar.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o",  # Mismo modelo para mantener coherencia en el tono, aunque el enfoque es más comercial.
)
# --- PASO 3: GESTIÓN DE WORKFLOWS Y RESOLUCIÓN DE CONFLICTOS ---

# Tarea 1: El Ingeniero evalúa y resuelve conflictos de presupuesto
tarea_analisis = Task(
    description=(
        "Un cliente quiere armar un PC con un procesador Ryzen 9, pero solo tiene $300.000 CLP de presupuesto. "
        "1. Analiza si este presupuesto es viable para un Ryzen 9. "
        "2. RESOLUCIÓN DE CONFLICTO: Si no es viable, diseña una alternativa realista dentro de ese presupuesto (ej. Ryzen 5 + Placa A320). "
        "3. Entrega un reporte técnico crudo con los componentes viables y precios estimados."
    ),
    expected_output="Reporte técnico con la validación del presupuesto y los componentes sugeridos como alternativa.",
    agent=ingeniero_hardware,
)

# Tarea 2: El Vendedor toma los datos y redacta el correo al cliente
tarea_ventas = Task(
    description=(
        "Toma el reporte del Ingeniero de Hardware. "
        "Redacta un correo amigable para el cliente explicando por qué el Ryzen 9 no es viable con su presupuesto, "
        "pero ofrécele la alternativa sugerida por el ingeniero de forma atractiva. "
        "Incluye una tabla con la cotización final."
    ),
    expected_output="Correo electrónico amigable en formato Markdown con la cotización.",
    agent=ejecutivo_ventas,
)

# Orquestación del Equipo (Workflow Secuencial)
equipo_hardibot = Crew(
    agents=[ingeniero_hardware, ejecutivo_ventas],
    tasks=[tarea_analisis, tarea_ventas],
    process=Process.sequential,  # El Vendedor espera a que el Ingeniero termine
)

if __name__ == "__main__":
    print("🚀 Iniciando Orquestación Multi-Agente (Back-office HardiBot)...\n")
    resultado_final = equipo_hardibot.kickoff()
    print("\n==============================================")
    print("📧 RESULTADO FINAL (Entregable al Cliente):")
    print("==============================================")
    print(resultado_final)
