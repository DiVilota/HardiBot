import streamlit as st
from src.observability import get_dashboard_metrics, estimar_ahorro_tokens
from src.db import listar_todas_cotizaciones


def render_admin():
    st.divider()
    st.markdown("**⚙️ Panel Admin**")

    with st.expander("📊 Dashboard LangSmith", expanded=False):
        render_langsmith_dashboard()

    with st.expander("📋 Todas las cotizaciones (Admin)", expanded=False):
        render_all_quotes()

    with st.expander("🔧 Traza de herramientas", expanded=False):
        render_tool_trace()


def render_langsmith_dashboard():
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


def render_all_quotes():
    todas = listar_todas_cotizaciones()
    if todas:
        for tc in todas:
            t_str = f"{tc['total_clp']:,}".replace(",", ".")
            st.caption(
                f"#{tc['id']} — **{tc['email']}** ({tc['persona_id']}) — "
                f"${t_str} CLP — {tc['created_at'][:10]}"
            )
    else:
        st.caption("Sin cotizaciones en el sistema")


def render_tool_trace():
    tool_history = st.session_state.get("tool_history", [])
    if not tool_history:
        st.caption("Sin ejecuciones en esta sesion")
        return
    for i, entry in enumerate(tool_history, 1):
        st.caption(f"**Paso {i}** — {entry['query'][:60]}...")
        for tc in entry["tools"]:
            icon = "OK" if tc["status"] == "complete" else "ERR"
            st.markdown(f"{icon} **`{tc['name']}`** — {tc['duration']}s")
