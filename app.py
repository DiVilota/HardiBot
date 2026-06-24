import time
import streamlit as st
from src.core import reconfigurar_agente, app_state
from src.personas import PERSONAS
from src.sesiones import cargar_historial
from src.db import obtener_usuario as db_obtener_usuario
from ui.theme import load_theme
from ui.login import render_login
from ui.sidebar import render_sidebar
from ui.chat import render_chat

AVATARS = {"hardware": "💻", "ferreteria": "🛠️", "repuestos": "🚗"}

st.set_page_config(page_title="HardiBot", layout="wide")

load_theme()

if st.session_state.get("sidebar_collapsed"):
    from ui.theme import inject_sidebar_collapsed_css
    inject_sidebar_collapsed_css()

if st.session_state.get("dark_mode"):
    from ui.theme import inject_dark_css
    inject_dark_css()

# ── Inicializar estado de sesion ──
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

# ── Auto-login via query param ──
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

# ── Login Gate ──
render_login()

# ── Header ──
persona_actual = PERSONAS[st.session_state.persona_id]
avatar = AVATARS.get(st.session_state.persona_id, "🤖")
st.title(f"{avatar} {persona_actual['nombre']}")
st.caption(persona_actual["descripcion"])

# ── Sidebar ──
render_sidebar()

# ── Chat ──
render_chat(avatar)
