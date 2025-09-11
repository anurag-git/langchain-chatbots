import streamlit as st
import chatbot_backend as demo_bot

st.title("Generative AI Chatbot using LLama3.2")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

input_text = st.chat_input("Use this chatbot powered by Llama3.2")
if input_text:
    with st.chat_message("user"):
        st.markdown(input_text)

    st.session_state.chat_history.append({"role": "user", "text": input_text})
    chat_response = demo_bot.demo_conversion(input_text=input_text)

    with st.chat_message("assistant"):
        st.markdown(chat_response.content)

    st.session_state.chat_history.append({"role": "assistant", "text": chat_response.content})

    