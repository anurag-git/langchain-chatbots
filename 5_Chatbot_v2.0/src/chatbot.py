"""
Pure AI service layer with no Streamlit dependencies.
Handles all AI model interactions and business logic.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_classic.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from functools import lru_cache
from huggingface_hub import InferenceClient
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

@dataclass
class ChatResponse:
    """Structured response from AI service"""
    message: str
    confidence: float = 1.0
    response_type: str = "standard"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatRequest:
    """Structured request to AI service"""
    user_input: str
    temperature: float = 0.7
    response_type: str = "standard"
    session_id: str = "default_session"


class ChatbotService:
    """Backend service for handling AI model interactions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['ai_model']['name']
        self.chatbot_name = config['chatbot']['name']
        self.repo= config['llm']['repo']
        self.api_token= config['llm']['api_token']
        self.api_endpoint= config['llm']['api_endpoint']
        self.store: Dict[str, InMemoryChatMessageHistory] = {}
        
    def get_model(self, temperature: float) -> ChatOllama:
        """Return the current AI model with specified temperature setting"""
        return ChatOllama(
            model=self.model_name,
            temperature=float(temperature)
        )

    def get_huggingface_model(self, temperature: float) -> ChatHuggingFace:
        """
        Return the Hugging Face LLM wrapper compatible with LangChain.
        """
        llm = HuggingFaceEndpoint(
            repo_id=self.repo, # Model name
            huggingfacehub_api_token=self.api_token,
            temperature=temperature,
            streaming=True
        )

        return ChatHuggingFace(llm=llm)

    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create session history for conversation management"""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]
    
    @lru_cache(maxsize=100)
    def _cached_response(self, full_prompt: str, temperature: float, session_id: str) -> str:
        """Internal cached response method"""
        chat_model = self.get_model(temperature)
        chat_with_history = RunnableWithMessageHistory(chat_model, self.get_session_history)
        
        response = chat_with_history.invoke(
            input=full_prompt,
            config={"configurable": {"session_id": session_id}}
        )

        return response.content if hasattr(response, 'content') else str(response)
        
    async def get_response(self, request: ChatRequest) -> ChatResponse:
        """
        Generate AI responses based on user input and settings
        Returns structured ChatResponse object
        """
        if not request.user_input:
            return ChatResponse(
                message="Please provide input for the chatbot.",
                confidence=0.0,
                response_type=request.response_type
            )
        
        try:
            # Create full prompt using prompt service
            full_prompt = PromptService.create_prompt(
                request.user_input, 
                request.response_type, 
                self.chatbot_name
            )
            
            # Get response using cached method
            response_content = self._cached_response(
                full_prompt, 
                request.temperature, 
                request.session_id
            )
            
            return ChatResponse(
                message=response_content,
                confidence=1.0,
                response_type=request.response_type,
                metadata={
                    "temperature": request.temperature,
                    "session_id": request.session_id,
                    "model": self.model_name
                }
            )
            
        except Exception as e:
            return ChatResponse(
                message=f"Error generating response: {str(e)}",
                confidence=0.0,
                response_type=request.response_type,
                metadata={"error": str(e)}
            )
    
    def _get_streaming_response(self, full_prompt: str, temperature: float, session_id: str):
        """Internal streaming response method (not cached)"""
        chat_model = self.get_model(temperature)
        chat_with_history = RunnableWithMessageHistory(chat_model, self.get_session_history)
        
        # Use stream for streaming responses
        return chat_with_history.stream(
            input=full_prompt,
            config={"configurable": {"session_id": "session_id"}}
        )

    def _get_huggingface_streaming_response(self, full_prompt: str, temperature: float):
        """Internal streaming response method (not cached)"""
        chat_model = self.get_huggingface_model(temperature)
        chat_with_history = RunnableWithMessageHistory(chat_model, self.get_session_history)
        
        # Use stream for streaming responses
        return chat_with_history.stream(
            input=full_prompt,
            config={"configurable": {"session_id": "session_id"}}
        )
    
    def get_response_stream(self, request: ChatRequest):
        """
        Generate streaming AI responses based on user input and settings
        Returns generator that yields response chunks
        """
        if not request.user_input:
            yield "Please provide input for the chatbot."
            return
        
        try:
            # Create full prompt using prompt service
            full_prompt = PromptService.create_prompt(
                request.user_input, 
                request.response_type, 
                self.chatbot_name
            )
            
            #####    code to use local model for streaming  #####
            # # Get streaming response (no caching for streams)
            # stream = self._get_streaming_response(
            #     full_prompt, 
            #     request.temperature, 
            #     request.session_id
            # )
            #####    code to use local model for streaming  #####

            # Get streaming response (no caching for streams)
            stream = self._get_huggingface_streaming_response(
                full_prompt, 
                request.temperature
            )

            # Yield each chunk from the stream
            for chunk in stream:
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
                    
        except Exception as e:
            yield f"Error generating response: {str(e)}"

class PromptService:
    """Service for handling prompt generation and formatting"""
    
    @staticmethod
    def create_prompt(user_input: str, response_type: str, chatbot_name: str) -> str:
        """Creates the formatted prompt for the LLM"""
        if not user_input:
            return None
            
        # Choose the AI's personality based on response type
        system_prompts = {
            "creative": f"You are {chatbot_name}, an imaginative AI assistant. Be creative and think outside the box while responding.",
            "factual": f"You are {chatbot_name}, a precise AI assistant. Stick to verified facts only. If unsure, explicitly state that.",
            "standard": f"You are {chatbot_name}, a helpful AI assistant."
        }
        
        system_prompt = SystemMessagePromptTemplate.from_template(
            system_prompts.get(response_type, system_prompts["standard"])
        )
        
        # Example conversations for context
        examples = [
            (
                "Can you introduce yourself?",
                f"Of course! I'm {chatbot_name}, your friendly AI helper. I'm here to answer your questions and assist you."
            ),
            (
                "What can you do for me?", 
                "I can answer your questions, help you brainstorm ideas, and explain concepts in simple terms."
            ),
            (
                "Tell me something fun about AI.",
                "Sure! Did you know some AIs can generate music or art, almost like human creativity?"
            )
        ]
        
        # Build message list
        messages = [system_prompt]
        
        for human_msg, ai_msg in examples:
            messages.extend([
                HumanMessagePromptTemplate.from_template(human_msg),
                AIMessagePromptTemplate.from_template(ai_msg)
            ])
        
        messages.append(HumanMessagePromptTemplate.from_template("{user_input}"))
        
        # Create and format prompt
        prompt_template = ChatPromptTemplate.from_messages(messages)
        return prompt_template.format(chatbot_name=chatbot_name, user_input=user_input)