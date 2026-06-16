import time
import streamlit as st
from src.core import ejecutar_con_streaming, reconfigurar_agente, app_state
from src.personas import PERSONAS
from src.observability import get_dashboard_metrics, estimar_ahorro_tokens
from src.sesiones import guardar_sesion, cargar_sesion, listar_sesiones, eliminar_sesion

st.set_page_config(page_title="HardiBot", layout="centered")

persona_actual = PERSONAS[st.session_state.get("persona_id", "hardware")]
st.title(f"🤖 {persona_actual['nombre']}")
st.caption(persona_actual["descripcion"])

PERSONA_IDS = list(PERSONAS.keys())

if "persona_id" not in st.session_state:
    st.session_state.persona_id = "hardware"
    st.session_state.tool_history = []
    st.session_state.session_id = f"sesion_{int(time.time())}"
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
    st.caption(f"Catalogo: `{persona_actual['catalogo']}`")

    # ── Cotizacion PDF ──
    st.divider()
    st.caption("**Cotizacion**")
    carrito = app_state.carrito
    if carrito.items:
        total = carrito.total()
        st.caption(f"Items: {len(carrito.items)} | Total: ${total:,.0f}".replace(",", "."))
        pdf_bytes = carrito.generar_pdf()
        st.download_button(
            label="Descargar cotizacion PDF",
            data=pdf_bytes,
            file_name="cotizacion_hardibot.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.caption("Carrito vacio")

    # ── Sesiones ──
    st.divider()
    with st.expander("Sesiones guardadas", expanded=False):
        sesiones = listar_sesiones()
        if sesiones:
            for s in sesiones:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"{s['persona_id']} — {s['mensajes']} msg", key=f"load_{s['session_id']}", use_container_width=True):
                        data = cargar_sesion(s['session_id'])
                        if data:
                            st.session_state.session_id = s['session_id']
                            st.session_state.persona_id = data.get('persona_id', 'hardware')
                            st.session_state.messages = data.get('messages', [])
                            st.session_state.tool_history = data.get('tool_history', [])
                            reconfigurar_agente(st.session_state.persona_id)
                            st.rerun()
                with col2:
                    if st.button("X", key=f"del_{s['session_id']}"):
                        eliminar_sesion(s['session_id'])
                        st.rerun()
        else:
            st.caption("Sin sesiones guardadas")

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
            status = st.status("Analizando tu consulta...", expanded=True)
            response_placeholder = st.empty()

            displayed = ""
            tool_calls = []
            metadata = {}

            for event in ejecutar_con_streaming(prompt):
                if event["type"] == "token":
                    displayed += event["content"]
                    response_placeholder.markdown(displayed + "▌")
                elif event["type"] == "tool_start":
                    status.markdown(f"🔄 **{event['name']}**")
                elif event["type"] == "tool_end":
                    duration = event.get("duration", "")
                    label = f"✅ **{event['name']}**"
                    if duration:
                        label += f" — {duration}s"
                    status.markdown(label)
                    if event.get("input"):
                        status.code(str(event["input"])[:120], language="text")
                elif event["type"] == "meta":
                    tool_calls = event["tool_calls"]
                    metadata = event["metadata"]

            status.update(
                label=f"Completado — {len(tool_calls)} herramienta(s) · {metadata.get('latencia', '?')}s",
                state="complete",
            )
            status.expanded = False

            response_placeholder.markdown(displayed)

            with st.expander("Arbol de decision del agente", expanded=False):
                st.caption(f"⏱ Latencia total: **{metadata.get('latencia', '?')}s**")
                if tool_calls:
                    for i, tc in enumerate(tool_calls, 1):
                        st.markdown(f"**Paso {i}: `{tc.get('name', '?')}`**")
                        col_in, col_out = st.columns([1, 1])
                        with col_in:
                            st.text_area("Input", tc.get("input", ""), height=60, key=f"in_{i}_{int(time.time())}", label_visibility="collapsed")
                        with col_out:
                            st.text_area("Output", str(tc.get("output", ""))[:200], height=60, key=f"out_{i}_{int(time.time())}", label_visibility="collapsed")
                        if tc.get("duration"):
                            st.caption(f"⏱ Duracion: {tc['duration']}s")

            st.session_state.tool_history.append({
                "query": prompt,
                "tools": tool_calls,
                "latencia": metadata.get("latencia", 0),
            })

        st.session_state.messages.append({"role": "assistant", "content": displayed})

        guardar_sesion(
            session_id=st.session_state.get("session_id", "default"),
            persona_id=st.session_state.persona_id,
            messages=st.session_state.messages,
            tool_history=st.session_state.tool_history,
            carrito_items=app_state.carrito.items,
        )
