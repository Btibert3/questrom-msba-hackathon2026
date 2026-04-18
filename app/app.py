import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("MSBA Hackathon 2026 — LLM Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            url = os.environ["MODAL_CHAT_URL"]
            payload = {"messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]}
            response = httpx.post(url, json=payload, timeout=120)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
