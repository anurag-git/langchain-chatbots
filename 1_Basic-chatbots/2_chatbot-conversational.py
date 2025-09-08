"""
What it does:
Creates a conversational AI that can handle back-and-forth dialogue
Uses a message system with different types of messages
Can maintain context and remember the conversation flow
"""

# Chat model for Ollama
from langchain_ollama import ChatOllama  
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize chat model
chat_model = ChatOllama(model="llama3.2", temperature=0.7)

# Define messages
messages = [
    SystemMessage(content="You are a helpful AI assistant."),
    HumanMessage(content="Explain generative AI in one sentence.")
]

# Get response using invoke
response = chat_model.invoke(messages)

# Print the response text
print(response.content)
