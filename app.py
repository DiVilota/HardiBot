import time
import streamlit as st
from src.core import ejecutar_con_streaming, reconfigurar_agente, app_state
from src.personas import PERSONAS
from src.observability import get_dashboard_metrics, estimar_ahorro_tokens
from src.sesiones import guardar_sesion, cargar_historial
from src.auth import verificar, registrar
from src.db import guardar_cotizacion, listar_cotizaciones, cargar_cotizacion, obtener_usuario as db_obtener_usuario

AVATARS = {"hardware": "💻", "ferreteria": "🛠️", "repuestos": "🚗"}

TOOL_MESSAGES = {
    "_buscar_catalogo_local": "📦 Revisando el inventario local...",
    "_buscar_web": "🌐 Buscando en tiendas online...",
    "_buscar_knasta": "🔍 Buscando en Knasta.cl...",
    "_calcular_presupuesto": "🧮 Calculando totales y descuentos...",
    "_buscar_foto_componente": "🖼️ Buscando imagen del producto...",
    "_agregar_al_carrito": "🛒 Agregando al carrito...",
    "_ver_carrito": "📋 Revisando el carrito...",
}

st.set_page_config(page_title="HardiBot", layout="centered")

PERSONA_IDS = list(PERSONAS.keys())

# ── Inicializar estado ──
for key, val in [
    ("persona_id", "hardware"),
    ("tool_history", []),
    ("session_id", f"sesion_{int(time.time())}"),
]:
    if key not in st.session_state:
        st.session_state[key] = val

if "messages" not in st.session_state:
    p = PERSONAS[st.session_state.persona_id]
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy {p['nombre']}. {p['descripcion']}"}
    ]

user = st.session_state.get("user", None)
es_admin = user and user.get("rol") == "admin"
avatar = AVATARS.get(st.session_state.persona_id, "🤖")

# ══════════════════════════════════════════════════════════
#  AUTO-LOGIN VIA QUERY PARAM (persiste al refrescar F5)
# ══════════════════════════════════════════════════════════
if "user" not in st.session_state:
    qp_email = st.query_params.get("user")
    if qp_email:
        u = db_obtener_usuario(qp_email)
        if u:
            st.session_state.user = {"email": u["email"], "nombre": u["nombre"], "rol": u["rol"]}
            h = cargar_historial(u["email"])
            if h:
                st.session_state.messages = h.get("messages", st.session_state.messages)
                st.session_state.tool_history = h.get("tool_history", [])
                st.session_state.persona_id = h.get("persona_id", "hardware")
                reconfigurar_agente(st.session_state.persona_id)
                if h.get("carrito_items"):
                    for item in h["carrito_items"]:
                        app_state.carrito.agregar(item["producto"], item["cantidad"], item["precio_unitario"])
            st.rerun()

# ══════════════════════════════════════════════════════════
#  LOGIN / REGISTER GATE
# ══════════════════════════════════════════════════════════
if not user:
    st.markdown("## 🔐 HardiBot")
    st.caption("Inicia sesion para guardar tu historial de cotizaciones")

    tab_login, tab_register = st.tabs(["Iniciar Sesion", "Crear Cuenta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Contrasena", type="password", key="login_password")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Entrar", use_container_width=True, type="primary"):
                    u = verificar(email, password)
                    if u:
                        st.session_state.user = u
                        st.query_params["user"] = email
                        h = cargar_historial(email)
                        if h:
                            st.session_state.messages = h.get("messages", st.session_state.messages)
                            st.session_state.tool_history = h.get("tool_history", [])
                            st.session_state.persona_id = h.get("persona_id", "hardware")
                            reconfigurar_agente(st.session_state.persona_id)
                            if h.get("carrito_items"):
                                for item in h["carrito_items"]:
                                    app_state.carrito.agregar(item["producto"], item["cantidad"], item["precio_unitario"])
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
            with col2:
                if st.form_submit_button("Soy visitante", use_container_width=True):
                    st.session_state.user = {"email": "anonimo", "nombre": "Visitante", "rol": "anonimo"}
                    st.query_params["user"] = "anonimo"
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            nombre = st.text_input("Nombre", key="reg_nombre")
            email_reg = st.text_input("Email", key="reg_email")
            password_reg = st.text_input("Contrasena", type="password", key="reg_password")
            if st.form_submit_button("Crear cuenta", use_container_width=True, type="primary"):
                if not nombre or not email_reg or not password_reg:
                    st.error("Completa todos los campos")
                elif "@" not in email_reg:
                    st.error("Email invalido")
                elif len(password_reg) < 4:
                    st.error("La contrasena debe tener al menos 4 caracteres")
                else:
                    nuevo = registrar(email_reg, password_reg, nombre)
                    if nuevo:
                        st.session_state.user = nuevo
                        st.query_params["user"] = email_reg
                        st.rerun()
                    else:
                        st.error("Este email ya esta registrado")

    st.stop()

# ══════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════
persona_actual = PERSONAS[st.session_state.persona_id]

st.title(f"{avatar} {persona_actual['nombre']}")
st.caption(persona_actual["descripcion"])

with st.sidebar:
    st.markdown("**Demo - Marca Blanca**")

    # Personas
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

    # Nueva sesion
    st.divider()
    if st.button("🧹 Nueva sesion", use_container_width=True, help="Limpiar chat, carrito e historial"):
        app_state.carrito.limpiar()
        st.session_state.messages = [
            {"role": "assistant", "content": f"¡Hola! Soy {persona_actual['nombre']}. {persona_actual['descripcion']}"}
        ]
        st.session_state.tool_history = []
        st.session_state.session_id = f"sesion_{int(time.time())}"
        st.rerun()

    # Usuario activo
    st.divider()
    st.caption(f"👤 **{user.get('nombre', 'Visitante')}**")
    st.caption(f"Persona activa: {persona_actual['nombre']}")

    # Cotizacion PDF
    st.divider()
    st.markdown("**📄 Cotizacion**")
    carrito = app_state.carrito
    if carrito.items:
        total = int(carrito.total())
        total_str = f"{total:,}".replace(",", ".")
        st.caption(f"Items: {len(carrito.items)} | Total: ${total_str} CLP")
        pdf_bytes = carrito.generar_pdf()
        if pdf_bytes.startswith(b"Error:"):
            st.warning(pdf_bytes.decode())
        else:
            st.download_button(
                label="📥 Descargar cotizacion PDF",
                data=pdf_bytes,
                file_name="cotizacion_hardibot.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.link_button(
            "📧 Enviar cotizacion a mi correo",
            "mailto:?subject=Cotizacion HardiBot&body=Adjunta el PDF descargado con tu cotizacion.",
            use_container_width=True,
        )
    else:
        st.caption("Carrito vacio")

    # Cerrar sesion
    st.divider()
    if user.get("email") != "anonimo":
        if st.button("🚪 Cerrar sesion", use_container_width=True):
            st.session_state.user = None
            st.query_params.clear()
            st.rerun()

    # ── Historial de cotizaciones ──
    if user.get("email") != "anonimo":
        st.divider()
        with st.expander("📋 Mis cotizaciones guardadas", expanded=False):
            cotizaciones = listar_cotizaciones(user["email"])
            if cotizaciones:
                for c in cotizaciones:
                    total_str = f"{c['total_clp']:,}".replace(",", ".")
                    label = f"Cotizacion #{c['id']} — ${total_str} CLP — {c['created_at'][:10]}"
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(label, key=f"cot_{c['id']}", use_container_width=True):
                            data = cargar_cotizacion(c['id'])
                            if data:
                                st.session_state.messages = data["mensajes"]
                                st.session_state.persona_id = data.get("persona_id", "hardware")
                                st.session_state.tool_history = []
                                reconfigurar_agente(st.session_state.persona_id)
                                app_state.carrito.limpiar()
                                for item in data["carrito_json"]:
                                    app_state.carrito.agregar(item["producto"], item["cantidad"], item["precio_unitario"])
                                st.rerun()
            else:
                st.caption("Sin cotizaciones guardadas")

    # ── Controles admin ──
    if es_admin:
        st.caption(f"Catalogo: `{persona_actual['catalogo']}`")

        with st.expander("📊 Dashboard LangSmith", expanded=False):
            metrics = get_dashboard_metrics()
            if metrics is None or metrics.get("status") == "no_api_key":
                st.caption("LangSmith no configurado")
                st.caption("Configura LANGCHAIN_API_KEY en .env")
            elif metrics.get("status") == "error":
                st.caption(f"Error: {metrics['mensaje']}")
            elif metrics.get("status") == "empty":
                st.caption("Sin ejecuciones recientes")
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
                    st.caption(f"Ahorro estimado: ~{ahorro['ahorro_estimado_tokens']} tokens")

        with st.expander("🔧 Traza de herramientas", expanded=False):
            if st.session_state.tool_history:
                for i, entry in enumerate(st.session_state.tool_history, 1):
                    st.caption(f"**Paso {i}** — {entry['query'][:60]}...")
                    for tc in entry["tools"]:
                        icon = "OK" if tc["status"] == "complete" else "ERR"
                        st.markdown(f"{icon} `{tc['name']}` — {tc['duration']}s")
            else:
                st.caption("Sin ejecuciones en esta sesion")

# ══════════════════════════════════════════════════════════
#  CHAT
# ══════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    role = msg["role"]
    msg_avatar = avatar if role == "assistant" else None
    with st.chat_message(role, avatar=msg_avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta aqui..."):
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
                "content": f"Persona no valida. Opciones: {', '.join(PERSONA_IDS)}"
            })
            st.rerun()
    else:
        cart_antes = len(app_state.carrito.items)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=avatar):
            status = st.status("Pensando...", expanded=True)
            response_placeholder = st.empty()

            displayed = ""
            tool_calls = []
            metadata = {}
            current_tool = None

            for event in ejecutar_con_streaming(prompt):
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

            if es_admin:
                with st.expander("Arbol de decision del agente", expanded=False):
                    st.caption(f"Latencia total: **{metadata.get('latencia', '?')}s**")
                    if tool_calls:
                        for i, tc in enumerate(tool_calls, 1):
                            st.markdown(f"**Paso {i}: `{tc.get('name', '?')}`**")
                            col_in, col_out = st.columns([1, 1])
                            with col_in:
                                st.text_area("Input", tc.get("input", ""), height=60, key=f"in_{i}_{int(time.time())}", label_visibility="collapsed")
                            with col_out:
                                st.text_area("Output", str(tc.get("output", ""))[:200], height=60, key=f"out_{i}_{int(time.time())}", label_visibility="collapsed")
                            if tc.get("duration"):
                                st.caption(f"Duracion: {tc['duration']}s")

            st.session_state.tool_history.append({
                "query": prompt,
                "tools": tool_calls,
                "latencia": metadata.get("latencia", 0),
            })

        st.session_state.messages.append({"role": "assistant", "content": displayed})

        guardar_sesion(
            user_email=user.get("email", "anonimo"),
            persona_id=st.session_state.persona_id,
            messages=st.session_state.messages,
            tool_history=st.session_state.tool_history,
            carrito_items=app_state.carrito.items,
        )

        guardar_cotizacion(
            email=user.get("email", "anonimo"),
            persona_id=st.session_state.persona_id,
            mensajes=st.session_state.messages,
            carrito_items=app_state.carrito.items,
            total_clp=int(app_state.carrito.total()),
        )

        if len(app_state.carrito.items) != cart_antes:
            st.rerun()
