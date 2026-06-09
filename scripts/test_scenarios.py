"""
test_scenarios.py — Batería de escenarios para probar el comportamiento del agente.

Uso:
    python scripts/test_scenarios.py                     # Ejecuta todos
    python scripts/test_scenarios.py --list               # Lista escenarios
    python scripts/test_scenarios.py --escenario 1,3,5   # Escenarios especificos
    python scripts/test_scenarios.py --persona ferreteria # Cambia a FerriBot
    python scripts/test_scenarios.py --dry-run            # Muestra solo las queries
"""

import os
import sys
import argparse
import time
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import app_state, reconfigurar_agente, ejecutar_con_visibilidad
from src.personas import PERSONAS


SCENARIOS = [
    # ── Sin herramientas (solo charla) ──
    {
        "id": 1,
        "nombre": "Saludo simple",
        "query": "Hola, ¿cómo estás?",
        "espera": "sin_herramientas",
        "descripcion": "El agente NO debe invocar herramientas. Solo responder.",
    },
    {
        "id": 2,
        "nombre": "Pregunta genérica",
        "query": "¿Cuál es la diferencia entre DDR4 y DDR5?",
        "espera": "sin_herramientas",
        "descripcion": "Pregunta de conocimiento general, sin tools.",
    },
    # ── Catálogo RAG ──
    {
        "id": 3,
        "nombre": "Cotización simple",
        "query": "Cotízame un Ryzen 5 5600G con una placa B550 y 16GB de RAM",
        "espera": "buscar_catalogo",
        "descripcion": "Debe usar buscar_catalogo para consultar inventario.",
    },
    {
        "id": 4,
        "nombre": "Producto inexistente",
        "query": "¿Tienen stock del Intel Core i9-15900K?",
        "espera": "buscar_catalogo",
        "descripcion": "Producto que no existe en el catalogo. Debe informar sin inventar.",
    },
    {
        "id": 5,
        "nombre": "Presupuesto inviable",
        "query": "Quiero un PC gamer con Ryzen 9 y RTX 4090, mi presupuesto es $200.000",
        "espera": "buscar_catalogo",
        "descripcion": "Presupuesto insuficiente. Debe sugerir alternativa realista.",
    },
    # ── Calculadora ──
    {
        "id": 6,
        "nombre": "Cálculo de total",
        "query": "Tengo estos precios: 150000 + 85000 + 32000, ¿cuánto es el total?",
        "espera": "calcular_presupuesto",
        "descripcion": "Operacion matematica. Debe usar calcular_presupuesto.",
    },
    # ── Carrito ──
    {
        "id": 7,
        "nombre": "Agregar al carrito",
        "query": "Agrega un Ryzen 5 5600G de $150.000 al carrito",
        "espera": "agregar_al_carrito",
        "descripcion": "Debe usar agregar_al_carrito con los parametros correctos.",
    },
    {
        "id": 8,
        "nombre": "Ver carrito",
        "query": "¿Qué tengo en mi carrito?",
        "espera": "ver_carrito",
        "descripcion": "Debe usar ver_carrito para mostrar el contenido.",
    },
    # ── Búsqueda web ──
    {
        "id": 9,
        "nombre": "Búsqueda web",
        "query": "Busca en internet el precio actual del Ryzen 5 5600G en el mercado chileno",
        "espera": "buscar_web",
        "descripcion": "Pide precio de competencia. Debe usar buscar_web.",
    },
    # ── Múltiples herramientas ──
    {
        "id": 10,
        "nombre": "Flujo completo cotización",
        "query": "Necesito un PC para edición de video. Cotízame un Ryzen 7 con 32GB de RAM y una RTX 3060. Dame el total.",
        "espera": "multiple",
        "descripcion": "Flujo completo: catalogo + calculo + posible imagen. Varias tools.",
    },
    {
        "id": 11,
        "nombre": "Compatibilidad",
        "query": "¿Es compatible un i9-14900K con una placa H610?",
        "espera": "buscar_catalogo",
        "descripcion": "Debe revisar catalogo y advertir sobre thermal throttling.",
    },
]


PERSONAS_TEST = list(PERSONAS.keys())


def ejecutar_escenario(esc, dry_run=False):
    """Ejecuta un escenario y muestra resultados."""
    if dry_run:
        print(f"  [{esc['id']:02d}] {esc['nombre']}")
        print(f"        Query: \"{esc['query']}\"")
        print(f"        Espera: {esc['espera']}")
        return

    print(f"\n{'='*70}")
    print(f"  [{esc['id']:02d}] {esc['nombre']}")
    print(f"  Query: \"{esc['query']}\"")
    print(f"  Esperado: {esc['espera']}")
    print(f"  Descripción: {esc['descripcion']}")
    print(f"{'='*70}")

    start = time.time()
    tool_calls, respuesta, metadata = ejecutar_con_visibilidad(prompt, session_id=f"test_{esc['id']}")
    elapsed = time.time() - start

    print(f"\n  ⏱ Latencia: {metadata['latencia']}s")
    print(f"  🔧 Herramientas usadas ({len(tool_calls)}):")
    if tool_calls:
        for tc in tool_calls:
            icon = "✅" if tc["status"] == "complete" else "❌"
            print(f"     {icon} {tc['name']} ({tc['duration']}s)")
            print(f"        Input: {tc['input'][:100]}")
    else:
        print("     (ninguna — respuesta directa del LLM)")

    print(f"\n  📝 Respuesta:\n{respuesta[:500]}")
    print(f"\n  {'─'*70}")

    esc["resultado"] = {
        "tool_calls": [t["name"] for t in tool_calls],
        "latencia": metadata["latencia"],
        "herramientas_usadas": len(tool_calls),
    }


def resumen_final(scenarios_ejecutados):
    print(f"\n\n{'='*70}")
    print("  📊 RESUMEN DE ESCENARIOS")
    print(f"{'='*70}")
    total = len(scenarios_ejecutados)
    with_herramientas = sum(1 for s in scenarios_ejecutados if s["resultado"]["herramientas_usadas"] > 0)
    without = total - with_herramientas
    latencia_total = sum(s["resultado"]["latencia"] for s in scenarios_ejecutados if s["resultado"]["latencia"])
    latencia_prom = latencia_total / total if total else 0
    total_herramientas = sum(s["resultado"]["herramientas_usadas"] for s in scenarios_ejecutados)

    for s in scenarios_ejecutados:
        tools_str = ", ".join(s["resultado"]["tool_calls"]) if s["resultado"]["tool_calls"] else "—"
        print(f"  [{s['id']:02d}] {s['nombre']:30s} | "
              f"Herramientas: {tools_str:40s} | "
              f"⏱ {s['resultado']['latencia']}s")

    print(f"\n  {'─'*70}")
    print(f"  Total escenarios: {total}")
    print(f"  Con herramientas: {with_herramientas}")
    print(f"  Sin herramientas:  {without}")
    print(f"  Total llamadas:    {total_herramientas}")
    print(f"  Latencia promedio: {latencia_prom:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Batería de escenarios para HardiBot")
    parser.add_argument("--list", action="store_true", help="Lista escenarios disponibles")
    parser.add_argument("--escenario", type=str, help="IDs separados por coma (ej: 1,3,5)")
    parser.add_argument("--persona", type=str, default="hardware", choices=PERSONAS_TEST,
                        help="Persona a usar (default: hardware)")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra queries sin ejecutar")
    args = parser.parse_args()

    if args.persona != app_state.persona_id:
        info = reconfigurar_agente(args.persona)
        print(f"🔄 Persona cambiada a: {info['nombre']}")

    if args.list:
        print(f"\n🧪 Escenarios disponibles ({len(SCENARIOS)}):\n")
        for esc in SCENARIOS:
            print(f"  [{esc['id']:02d}] {esc['nombre']:30s} → {esc['espera']}")
            print(f"       {esc['descripcion']}")
        return

    escenarios_a_ejecutar = SCENARIOS
    if args.escenario:
        ids = [int(x.strip()) for x in args.escenario.split(",")]
        escenarios_a_ejecutar = [s for s in SCENARIOS if s["id"] in ids]

    print(f"\n{'='*70}")
    print(f"  🧪 HardiBot — Batería de Pruebas ({len(escenarios_a_ejecutar)} escenarios)")
    print(f"  Persona: {args.persona}")
    print(f"{'='*70}")

    for esc in escenarios_a_ejecutar:
        global prompt
        prompt = esc["query"]
        ejecutar_escenario(esc, dry_run=args.dry_run)

    if not args.dry_run:
        resumen_final(escenarios_a_ejecutar)


if __name__ == "__main__":
    main()
