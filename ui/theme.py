import streamlit as st
from pathlib import Path


def load_theme():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"style.css not found at {css_path}")


def inject_dark_css():
    st.markdown("""
    <style>
    .stApp,.stMain,.stApp>header{background:#0F172A!important}
    .stApp *{color-scheme:dark}
    [data-testid="stSidebar"]{background:#020617!important}
    [data-testid="stSidebar"] *{color:#CBD5E1!important}
    [data-testid="stSidebar"] button{background:#0F172A!important;border-color:#1E293B!important;color:#E2E8F0!important}
    [data-testid="stSidebar"] button:hover{background:#1E293B!important;color:#60A5FA!important}
    [data-testid="stSidebar"] [data-testid="stExpander"]{background:#0F172A!important;border-color:#1E293B!important}
    [data-testid="stSidebar"] hr{border-color:#334155!important}
    [data-testid="stChatMessage"]{background:#1E293B!important;border-color:#334155!important}
    [data-testid="stChatMessage"] *{color:#F1F5F9!important}
    [data-testid="stChatInput"] textarea{background:#1E293B!important;color:#F1F5F9!important;border-color:#334155!important}
    [data-testid="stChatInput"] textarea::placeholder{color:#64748B!important}
    button{background:#1E293B!important;color:#E2E8F0!important;border-color:#334155!important}
    button:hover{background:#334155!important;border-color:#60A5FA!important;color:#60A5FA!important}
    button[kind="primary"]{background:#3B82F6!important;color:#fff!important}
    button[kind="primary"]:hover{background:#2563EB!important}
    [data-testid="stExpander"]{background:#1E293B!important;border-color:#334155!important}
    [data-testid="stMetric"]{background:#1E293B!important;border-color:#334155!important}
    [data-testid="stMetricValue"]{color:#F1F5F9!important}
    [data-testid="stMetricLabel"]{color:#94A3B8!important}
    .stDownloadButton button{background:#1E293B!important;color:#E2E8F0!important;border-color:#60A5FA!important}
    .stDownloadButton button:hover{background:#1E293B!important;border-color:#3B82F6!important}
    .stLinkButton button{background:transparent!important;color:#60A5FA!important;border-color:#334155!important}
    input,textarea{background:#1E293B!important;color:#F1F5F9!important;border-color:#334155!important}
    input::placeholder,textarea::placeholder{color:#64748B!important}
    [data-baseweb="tab-list"]{background:#1E293B!important}
    [data-baseweb="tab"]{color:#94A3B8!important}
    [data-baseweb="tab"][aria-selected="true"]{background:#334155!important;color:#F1F5F9!important}
    p,span,label,div,caption{color:#E2E8F0!important}
    a{color:#60A5FA!important}
    h1,h2,h3,h4{color:#F1F5F9!important}
    hr{border-color:#334155!important}
    .login-container{background:#1E293B!important;border-color:#334155!important}
    .welcome-card{background:#1E293B!important;border-color:#334155!important}
    .skeleton{background:#334155!important}
    ::-webkit-scrollbar-thumb{background:#475569!important}
    ::-webkit-scrollbar-track{background:#1E293B!important}
    </style>
    """, unsafe_allow_html=True)


def inject_sidebar_collapsed_css():
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important}
    [data-testid="stSidebarCollapsedControl"]{display:none!important}
    .stMain .block-container{padding-left:1.5rem!important;max-width:100%!important}
    </style>
    """, unsafe_allow_html=True)
