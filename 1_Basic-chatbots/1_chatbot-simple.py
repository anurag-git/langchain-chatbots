"""
What it does:
Creates a basic AI model that responds to single questions
You give it a prompt (question), it gives you an answer
It's like asking a one-off question to someone who has no memory of previous conversations
"""
# New import for Ollama models
from langchain_ollama import OllamaLLM  

# Initialize local Ollama model
llm = OllamaLLM(model="llama3.2", temperature=0.7)

# Run prompt using the new invoke method
prompt = "Explain generative AI in one sentence."
response = llm.invoke(prompt)

# Print the response
print(response)

