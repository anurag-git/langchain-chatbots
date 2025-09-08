from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

def demo_chatbot():
    demo_llm = Ollama(model="llama3.2", temperature=0.4, top_p=0.5)
    return demo_llm

def demo_memory():
    llm_d = demo_chatbot()
    memory = ConversationBufferMemory(llm=llm_d, max_token_limit=500)
    return memory

def demo_conversion(input_text, memory):
    llm_chain_data = demo_chatbot()
    llm_conversation = ConversationChain(llm=llm_chain_data, memory=memory, verbose=True)
    chat_reply = llm_conversation.predict(input=input_text)
    return chat_reply

