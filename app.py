import streamlit as st
from src.core import chat_hardibot_stream_sync, reconfigurar_agente
from src.personas import PERSONAS

st.set_page_config(page_title="HardiBot", layout="centered")

persona_actual = PERSONAS[st.session_state.get("persona_id", "hardware")]
st.title(persona_actual["nombre"])
st.caption(persona_actual["descripcion"])

PERSONA_IDS = list(PERSONAS.keys())

if "persona_id" not in st.session_state:
    st.session_state.persona_id = "hardware"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy {persona_actual['nombre']}. {persona_actual['descripcion']}"}
    ]

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
                    st.rerun()

    st.divider()
    st.caption(f"Persona activa: **{persona_actual['nombre']}**")
    st.caption(f"Catalogo: `{persona_actual['catalogo']}`")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
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
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Persona no valida. Opciones: {', '.join(PERSONA_IDS)}"})
            st.rerun()
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = st.write_stream(chat_hardibot_stream_sync(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
