from langchain_ollama import ChatOllama
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def demo_chatbot():
    demo_llm = ChatOllama(model="llama3.2", temperature=0.7, top_p=0.5)  # Changed to ChatOllama
    return demo_llm

def demo_conversion(input_text):
    llm_chain_data = demo_chatbot()
    llm_conversation = RunnableWithMessageHistory(llm_chain_data, get_session_history)
    chat_reply = llm_conversation.invoke(
        input_text,
        config={"configurable": {"session_id": "default_session"}}
    )
    return chat_reply
