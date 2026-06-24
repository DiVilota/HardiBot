import time
import streamlit as st
from src.core import ejecutar_con_streaming, reconfigurar_agente, app_state
from src.sesiones import guardar_sesion
from src.db import guardar_cotizacion
from src.personas import PERSONA_IDS


TOOL_MESSAGES = {
    "_buscar_catalogo_local": "📦 Revisando el inventario local...",
    "_buscar_web": "🌐 Buscando en tiendas online...",
    "_buscar_knasta": "🔍 Buscando en Knasta.cl...",
    "_calcular_presupuesto": "🧮 Calculando totales y descuentos...",
    "_buscar_foto_componente": "🖼️ Buscando imagen del producto...",
    "_agregar_al_carrito": "🛒 Agregando al carrito...",
    "_ver_carrito": "📋 Revisando el carrito...",
}


def render_chat(avatar):
    user = st.session_state.get("user", {})
    es_admin = user.get("rol") == "admin"

    # ── Boton expandir sidebar ──
    if st.session_state.get("sidebar_collapsed"):
        col_exp, _ = st.columns([0.18, 0.82])
        with col_exp:
            if st.button("▶ Mostrar panel", key="expand_sidebar_btn", help="Mostrar barra lateral", use_container_width=True):
                st.session_state.sidebar_collapsed = False
                st.rerun()

    # ── Render message history ──
    for msg in st.session_state.messages:
        role = msg["role"]
        msg_avatar = avatar if role == "assistant" else None
        with st.chat_message(role, avatar=msg_avatar):
            st.markdown(msg["content"])

    # ── Chat input ──
    prompt = st.chat_input("Escribe tu consulta aqui...")

    if not prompt:
        return

    # ── Command handling ──
    if prompt.startswith("/persona "):
        _handle_persona_command(prompt)
        return

    cart_antes = len(app_state.carrito.items)

    history = [(m["role"], m["content"]) for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=avatar):
        displayed, tool_calls, metadata = _stream_response(es_admin, prompt, history)

        # ── Admin: decision tree ──
        if es_admin and tool_calls:
            with st.expander("Arbol de decision del agente", expanded=False):
                st.caption(f"Latencia total: **{metadata.get('latencia', '?')}s**")
                for i, tc in enumerate(tool_calls, 1):
                    st.markdown(f"**Paso {i}: `{tc.get('name', '?')}`**")
                    col_in, col_out = st.columns([1, 1])
                    with col_in:
                        st.text_area(
                            "Input", tc.get("input", ""), height=60,
                            key=f"in_{i}_{int(time.time())}",
                            label_visibility="collapsed",
                        )
                    with col_out:
                        st.text_area(
                            "Output", str(tc.get("output", ""))[:200], height=60,
                            key=f"out_{i}_{int(time.time())}",
                            label_visibility="collapsed",
                        )
                    if tc.get("duration"):
                        st.caption(f"Duracion: {tc['duration']}s")

        st.session_state.tool_history.append({
            "query": prompt,
            "tools": tool_calls,
            "latencia": metadata.get("latencia", 0),
        })

    st.session_state.messages.append({"role": "assistant", "content": displayed})

    _persistir(user, cart_antes)


def _stream_response(es_admin, prompt, history):
    status = st.status("Pensando...", expanded=True)
    response_placeholder = st.empty()

    displayed = ""
    tool_calls = []
    metadata = {}
    current_tool = None

    for event in ejecutar_con_streaming(prompt, history=history):
        if event["type"] == "token":
            displayed += event["content"]
            response_placeholder.markdown(displayed + "▌")
        elif event["type"] == "tool_start":
            tool_name = event.get("name", "")
            current_tool = tool_name
            friendly = TOOL_MESSAGES.get(tool_name, f"🔄 {tool_name}")
            if es_admin:
                status.markdown(f"🔄 **{tool_name}**")
            else:
                status.update(label=friendly, state="running")
        elif event["type"] == "tool_end":
            if es_admin:
                duration = event.get("duration", "")
                label = f"✅ **{current_tool or event.get('name', '')}**"
                if duration:
                    label += f" — {duration}s"
                status.markdown(label)
                if event.get("input"):
                    status.code(str(event["input"])[:120], language="text")
            current_tool = None
        elif event["type"] == "meta":
            tool_calls = event["tool_calls"]
            metadata = event["metadata"]

    if es_admin:
        status.update(
            label=f"Completado — {len(tool_calls)} herramienta(s) · {metadata.get('latencia', '?')}s",
            state="complete",
        )
    else:
        status.update(label="✅ Listo", state="complete")
    status.expanded = False

    response_placeholder.markdown(displayed)
    return displayed, tool_calls, metadata


def _handle_persona_command(prompt):
    pid = prompt.split(" ", 1)[1].strip().lower()
    if pid in PERSONA_IDS:
        info = reconfigurar_agente(pid)
        st.session_state.persona_id = pid
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Cambiado a **{info['nombre']}**. {info['titulo']}",
        }]
        st.session_state.tool_history = []
        st.rerun()
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Persona no valida. Opciones: {', '.join(PERSONA_IDS)}",
        })
        st.rerun()


def _persistir(user, cart_antes):
    guardar_sesion(
        user_email=user.get("email", "anonimo"),
        persona_id=st.session_state.persona_id,
        messages=st.session_state.messages,
        tool_history=st.session_state.tool_history,
        carrito_items=app_state.carrito.items,
    )

    if app_state.carrito.items:
        guardar_cotizacion(
            email=user.get("email", "anonimo"),
            persona_id=st.session_state.persona_id,
            mensajes=st.session_state.messages,
            carrito_items=app_state.carrito.items,
            total_clp=int(app_state.carrito.total()),
        )

    if len(app_state.carrito.items) != cart_antes:
        st.rerun()
