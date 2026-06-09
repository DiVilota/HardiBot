import time
import streamlit as st
from src.core import ejecutar_con_visibilidad, reconfigurar_agente
from src.personas import PERSONAS
from src.observability import get_dashboard_metrics, estimar_ahorro_tokens

st.set_page_config(page_title="HardiBot", layout="centered")

persona_actual = PERSONAS[st.session_state.get("persona_id", "hardware")]
st.title(f"🤖 {persona_actual['nombre']}")
st.caption(persona_actual["descripcion"])

PERSONA_IDS = list(PERSONAS.keys())

if "persona_id" not in st.session_state:
    st.session_state.persona_id = "hardware"
    st.session_state.tool_history = []
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy {persona_actual['nombre']}. {persona_actual['descripcion']}"}
    ]

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Demo - Marca Blanca**")
    cols = st.columns(len(PERSONA_IDS))
    for i, pid in enumerate(PERSONA_IDS):
        p = PERSONAS[pid]
        with cols[i]:
            if st.button(p["nombre"], key=f"btn_{pid}", help=f"Cambiar a {p['descripcion']}"):
                if st.session_state.persona_id != pid:
                    info = reconfigurar_agente(pid)
                    st.session_state.persona_id = pid
                    st.session_state.messages = [
                        {"role": "assistant", "content": f"¡Hola! Soy {info['nombre']}. {PERSONAS[pid]['descripcion']}"}
                    ]
                    st.session_state.tool_history = []
                    st.rerun()

    st.divider()
    st.caption(f"Persona activa: **{persona_actual['nombre']}**")
    st.caption(f"Catálogo: `{persona_actual['catalogo']}`")
    st.caption(f"Productos: {persona_actual.get('total_productos', 'N/A')}")

    # ── Dashboard LangSmith ──
    st.divider()
    with st.expander("📊 Dashboard de Transparencia (LangSmith)", expanded=False):
        metrics = get_dashboard_metrics()
        if metrics is None or metrics.get("status") == "no_api_key":
            st.caption("🔑 LangSmith no configurado")
            st.caption("Configura LANGCHAIN_API_KEY en .env")
        elif metrics.get("status") == "error":
            st.caption(f"⚠️ Error: {metrics['mensaje']}")
        elif metrics.get("status") == "empty":
            st.caption("📭 No hay ejecuciones recientes")
            st.caption("Envía un mensaje para ver métricas aquí")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Ejecuciones", metrics["total_ejecuciones"])
                st.metric("Latencia promedio", f'{metrics["latencia_promedio"]}s')
            with col2:
                st.metric("Tokens totales", metrics["total_tokens"])
                st.metric("Con error", metrics["ejecuciones_con_error"])

            col3, col4 = st.columns(2)
            with col3:
                st.metric("Latencia min", f'{metrics["latencia_min"]}s')
            with col4:
                st.metric("Latencia max", f'{metrics["latencia_max"]}s')

            ahorro = estimar_ahorro_tokens(metrics)
            if ahorro:
                st.caption(f"💡 Ahorro estimado: ~{ahorro['ahorro_estimado_tokens']} tokens ({ahorro['ahorro_estimado_porcentaje']}%)")

    # ── Historial de herramientas (sesión actual) ──
    st.divider()
    with st.expander("🔧 Traza de herramientas (esta sesión)", expanded=False):
        if st.session_state.tool_history:
            for i, entry in enumerate(st.session_state.tool_history, 1):
                st.caption(f"**Paso {i}** — {entry['query'][:60]}...")
                for tc in entry["tools"]:
                    icon = "✅" if tc["status"] == "complete" else "❌"
                    st.markdown(f"{icon} `{tc['name']}` — {tc['duration']}s")
        else:
            st.caption("Aún no hay ejecuciones en esta sesión")

# ── Chat ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    if prompt.startswith("/persona "):
        pid = prompt.split(" ", 1)[1].strip().lower()
        if pid in PERSONA_IDS:
            info = reconfigurar_agente(pid)
            st.session_state.persona_id = pid
            st.session_state.messages = [
                {"role": "assistant", "content": f"Cambiado a **{info['nombre']}**. {info['titulo']}"}
            ]
            st.session_state.tool_history = []
            st.rerun()
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Persona no válida. Opciones: {', '.join(PERSONA_IDS)}"
            })
            st.rerun()
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # ── Fase 1: Ejecución con visibilidad de herramientas ──
            status = st.status("🔍 Analizando tu consulta...", expanded=True)
            tool_calls, response, metadata = ejecutar_con_visibilidad(prompt)

            # Mostrar herramientas usadas
            if tool_calls:
                for tc in tool_calls:
                    icon = "✅" if tc["status"] == "complete" else "⏳"
                    label = f"**{tc['name']}**"
                    if tc["duration"]:
                        label += f" — ⏱ {tc['duration']}s"
                    status.markdown(f"{icon} {label}")
                    if tc["input"]:
                        status.code(tc["input"][:120], language="text")

            status.update(
                label=f"✅ Análisis completado — {len(tool_calls)} herramienta(s) · {metadata['latencia']}s",
                state="complete",
            )
            status.expanded = False

            # ── Fase 2: Streaming de la respuesta ──
            response_placeholder = st.empty()
            displayed = ""
            for palabra in response.split(" "):
                displayed += palabra + " "
                response_placeholder.markdown(displayed + "▌")
                time.sleep(0.015)
            response_placeholder.markdown(displayed)

            # ── Fase 3: Dashboard de transparencia de la ejecución ──
            with st.expander("🕵️ Árbol de decisión del agente", expanded=False):
                st.caption(f"⏱ Latencia total: **{metadata['latencia']}s**")
                for i, tc in enumerate(tool_calls, 1):
                    st.markdown(f"**Paso {i}: `{tc['name']}`**")
                    col_in, col_out = st.columns([1, 1])
                    with col_in:
                        st.text_area("Input", tc["input"], height=60, key=f"in_{i}_{int(time.time())}", label_visibility="collapsed")
                    with col_out:
                        st.text_area("Output", tc["output"][:200], height=60, key=f"out_{i}_{int(time.time())}", label_visibility="collapsed")
                    if tc["duration"]:
                        st.caption(f"⏱ Duración: {tc['duration']}s")

            # Guardar en el historial de herramientas de la sesión
            st.session_state.tool_history.append({
                "query": prompt,
                "tools": tool_calls,
                "latencia": metadata["latencia"],
            })

        st.session_state.messages.append({"role": "assistant", "content": response})
