# =============== IMPORTING REQUIRED LIBRARIES ===============
from langchain_ollama import ChatOllama
from langchain_classic.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import streamlit as st

class AIService:
    """Backend service for handling AI model interactions"""
    
    store = {}

    def __init__(self):
        self.model_name = "llama3.2"
    
    def get_model(self, temperature:float):
        """Return the current AI model with specified temperature setting"""
        # Create a new instance of the AI chat model
        model = ChatOllama(
            model=self.model_name,
            temperature=float(temperature)
        )
        
        return model
    
    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]
    
    # @st.cache_data tells Streamlit to cache this function's output to improve performance
    @st.cache_data
    def get_response(_self, full_prompt: str, temperature: float):
        """
        Generate AI responses based on user input and settings
        Parameters:
            full_prompt: The text input from the user + system prompt
            temperature: Controls AI creativity (0.0 = focused, 1.0 = creative)
        """
        # Return None if no prompt is provided
        if not full_prompt:
            return None
        
        # Create a new instance of the AI chat model      
        chat_model = _self.get_model(temperature)

        # Maintain chat history per session
        chat_with_history = RunnableWithMessageHistory(chat_model, _self.get_session_history)
        response = chat_with_history.invoke(
            input=full_prompt,
            config={"configurable": {"session_id": "default_session"}}
        )

        return response


class PromptService:
    """Service for handling prompt generation and formatting"""
    
    @staticmethod
    def create_prompt(user_input: str, response_type: str, chatbot_name: str) -> str:
        """Creates the prompt for the LLM."""
        
        # Return None if no user input is provided
        if not user_input:
            return None
        
        # Choose the AI's personality based on response type
        if response_type == "creative":
            system_prompt = SystemMessagePromptTemplate.from_template("You are {chatbot_name}, an imaginative AI assistant. Be creative and think outside the box while responding.")
        elif response_type == "factual":
            system_prompt = SystemMessagePromptTemplate.from_template("You are {chatbot_name}, a precise AI assistant. Stick to verified facts only. If unsure, explicitly state that.")
        else:  # standard response type
            system_prompt = SystemMessagePromptTemplate.from_template("You are {chatbot_name}, a helpful AI assistant.")
        
        # Example 1
        example_human1 = HumanMessagePromptTemplate.from_template("Can you introduce yourself?")
        example_ai1 = AIMessagePromptTemplate.from_template(
            "Of course! I'm {chatbot_name}, your friendly AI helper. I’m here to answer your questions and assist you."
        )

        # Example 2
        example_human2 = HumanMessagePromptTemplate.from_template("What can you do for me?")
        example_ai2 = AIMessagePromptTemplate.from_template(
            "I can answer your questions, help you brainstorm ideas, and explain concepts in simple terms."
        )

        # Example 3
        example_human3 = HumanMessagePromptTemplate.from_template("Tell me something fun about AI.")
        example_ai3 = AIMessagePromptTemplate.from_template(
            "Sure! Did you know some AIs can generate music or art, almost like human creativity?"
        )

        # Placeholder for real user input
        human_message = HumanMessagePromptTemplate.from_template("{user_input}")

        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            system_prompt,
            example_human1, example_ai1,
            example_human2, example_ai2,
            example_human3, example_ai3,
            human_message
        ])

        prompt = prompt_template.format(chatbot_name=chatbot_name, user_input=user_input)
        return prompt

