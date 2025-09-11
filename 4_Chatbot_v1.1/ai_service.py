# =============== IMPORTING REQUIRED LIBRARIES ===============
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import streamlit as st

class AIService:
    """Backend service for handling AI model interactions"""
    
    def __init__(self):
        self.model_name = "llama3.2"
    
    @st.cache_data
    def get_response(self, full_prompt: str, temperature: float):
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
        chat_model = ChatOllama(
            model=self.model_name,
            temperature=float(temperature)
        )
        
        # Send the messages to the AI and get its response
        response = chat_model.invoke(input=full_prompt)
        return response


class PromptService:
    """Service for handling prompt generation and formatting"""
    
    @staticmethod
    def create_prompt(user_prompt: str, response_type: str) -> str:
        """Creates the prompt for the LLM."""
        
        # Return None if no user input is provided
        if not user_prompt:
            return None
        
        # Choose the AI's personality based on response type
        if response_type == "creative":
            system_prompt = "You are an imaginative AI assistant. Be creative and think outside the box while responding."
        elif response_type == "factual":
            system_prompt = "You are a precise AI assistant. Stick to verified facts only. If unsure, explicitly state that."
        else:  # standard response type
            system_prompt = "You are a helpful AI assistant."
        
        # Structure the conversation with system instructions and user input
        input_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        return input_messages

