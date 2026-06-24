import streamlit as st
from src.auth import verificar, registrar
from src.sesiones import cargar_historial
from src.core import reconfigurar_agente, app_state
from src.db import obtener_usuario as db_obtener_usuario


def render_login():
    """Login gate con card centrada y tabs responsive."""

    if st.session_state.get("user"):
        return True

    st.markdown("""
    <div class="login-container">
      <div class="login-logo">🤖</div>
      <div class="login-title">HardiBot</div>
      <div class="login-subtitle">Tu asistente inteligente de cotizaciones</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Iniciar Sesion", "Crear Cuenta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input(
                "Email", key="login_email",
                placeholder="tu@email.com",
                label_visibility="collapsed",
            )
            password = st.text_input(
                "Contrasena", type="password", key="login_password",
                placeholder="Contrasena",
                label_visibility="collapsed",
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                login_btn = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            with col2:
                guest_btn = st.form_submit_button("Soy visitante", use_container_width=True)

            if login_btn:
                u = verificar(email, password)
                if u:
                    _set_user_session(u)
                    st.query_params["user"] = email
                    _restaurar_sesion(u["email"])
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

            if guest_btn:
                st.session_state.user = {"email": "anonimo", "nombre": "Visitante", "rol": "anonimo"}
                st.query_params["user"] = "anonimo"
                st.rerun()

    with tab_register:
        with st.form("register_form"):
            nombre = st.text_input(
                "Nombre", key="reg_nombre",
                placeholder="Tu nombre completo",
                label_visibility="collapsed",
            )
            email_reg = st.text_input(
                "Email", key="reg_email",
                placeholder="tu@email.com",
                label_visibility="collapsed",
            )
            password_reg = st.text_input(
                "Contrasena", type="password", key="reg_password",
                placeholder="Minimo 4 caracteres",
                label_visibility="collapsed",
            )
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


def _set_user_session(u):
    st.session_state.user = {
        "email": u["email"],
        "nombre": u.get("nombre", u["email"]),
        "rol": u.get("rol", "anonimo"),
    }


def _restaurar_sesion(email):
    h = cargar_historial(email)
    if not h:
        return
    if h.get("messages"):
        st.session_state.messages = h["messages"]
    if h.get("tool_history"):
        st.session_state.tool_history = h["tool_history"]
    persona_id = h.get("persona_id", "hardware")
    st.session_state.persona_id = persona_id
    reconfigurar_agente(persona_id)
    if h.get("carrito_items"):
        app_state.carrito.limpiar()
        for item in h["carrito_items"]:
            app_state.carrito.agregar(
                item["producto"], item["cantidad"], item["precio_unitario"]
            )
