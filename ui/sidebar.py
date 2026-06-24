import time
import streamlit as st
from src.personas import PERSONAS, PERSONA_IDS
from src.core import reconfigurar_agente, app_state
from src.db import listar_cotizaciones, cargar_cotizacion, eliminar_cotizacion
from ui.admin import render_admin


AVATARS = {"hardware": "💻", "ferreteria": "🛠️", "repuestos": "🚗"}


def render_sidebar():
    user = st.session_state.get("user", {})
    es_admin = user.get("rol") == "admin"
    persona_actual = PERSONAS[st.session_state.persona_id]
    avatar = AVATARS.get(st.session_state.persona_id, "🤖")

    # ── User info ──
    with st.sidebar:
        st.markdown("### HardiBot v3.0")

        # ── Persona selector ──
        st.markdown("**Asistente activo**")
        cols = st.columns(len(PERSONA_IDS))
        for i, pid in enumerate(PERSONA_IDS):
            p = PERSONAS[pid]
            with cols[i]:
                icon = AVATARS.get(pid, "🤖")
                if st.button(
                    f"{icon} {p['nombre']}",
                    key=f"btn_{pid}",
                    help=f"Cambiar a {p['descripcion']}",
                    use_container_width=True,
                ):
                    if st.session_state.persona_id != pid:
                        info = reconfigurar_agente(pid)
                        st.session_state.persona_id = pid
                        st.session_state.messages = [{
                            "role": "assistant",
                            "content": f"¡Hola! Soy {info['nombre']}. {PERSONAS[pid]['descripcion']}",
                        }]
                        st.session_state.tool_history = []
                        st.rerun()

        st.divider()

        # ── Nueva sesion ──
        if st.button("🧹 Nueva sesion", use_container_width=True):
            app_state.carrito.limpiar()
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"¡Hola! Soy {persona_actual['nombre']}. {persona_actual['descripcion']}",
            }]
            st.session_state.tool_history = []
            st.session_state.session_id = f"sesion_{int(time.time())}"
            st.rerun()

        st.divider()

        # ── User badge ──
        st.caption(f"👤 **{user.get('nombre', 'Visitante')}**")
        st.caption(f"🤖 Persona: {persona_actual['nombre']}")
        if es_admin:
            st.caption(f"📂 Catalogo: `{persona_actual['catalogo']}`")

        st.divider()

        # ── Carrito / Cotizacion ──
        _render_cart_section()

        # ── Cerrar sesion ──
        st.divider()
        if user.get("email") != "anonimo":
            if st.button("🚪 Cerrar sesion", use_container_width=True):
                st.session_state.user = None
                st.query_params.clear()
                st.rerun()

        # ── Historial de cotizaciones ──
        if user.get("email") != "anonimo":
            _render_quote_history(user["email"])

        # ── Admin ──
        if es_admin:
            render_admin()

        return avatar


def _render_cart_section():
    st.markdown("**📄 Cotizacion**")
    carrito = app_state.carrito

    if not carrito.items:
        st.caption("Carrito vacio")
        return

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


def _render_quote_history(email):
    with st.expander("📋 Mis cotizaciones guardadas", expanded=False):
        cotizaciones = listar_cotizaciones(email)
        if not cotizaciones:
            st.caption("Sin cotizaciones guardadas")
            return

        for c in cotizaciones:
            total_str = f"{c['total_clp']:,}".replace(",", ".")
            label = f"Cotizacion #{c['id']} — ${total_str} CLP — {c['created_at'][:10]}"
            col1, col2, col3 = st.columns([3, 1, 0.5])
            with col1:
                if st.button(label, key=f"cot_{c['id']}", use_container_width=True):
                    data = cargar_cotizacion(c["id"])
                    if data:
                        st.session_state.messages = data["mensajes"]
                        st.session_state.persona_id = data.get("persona_id", "hardware")
                        st.session_state.tool_history = []
                        reconfigurar_agente(st.session_state.persona_id)
                        app_state.carrito.limpiar()
                        for item in data["carrito_json"]:
                            app_state.carrito.agregar(
                                item["producto"], item["cantidad"], item["precio_unitario"]
                            )
                        st.rerun()
            with col2:
                st.caption(f"{c['persona_id']}")
            with col3:
                if st.button("🗑️", key=f"del_{c['id']}", help="Eliminar cotizacion"):
                    eliminar_cotizacion(c["id"], email)
                    st.rerun()



