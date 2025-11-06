"""
Pure AI service layer with no Streamlit dependencies.
Handles all AI model interactions and business logic.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_classic.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
import certifi, os

# Set up SSL certificates
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

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
        self.search_tools = self._initialize_search_tools()
        self.agent_executor = None  # Lazy initialization
        
    
    def _initialize_search_tools(self) -> List:
        """Initialize search tools for the agent"""
        
        # FIX: Set certificate path
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

        # Create instance ONCE
        search = DuckDuckGoSearchRun()
        
        @tool
        def internet_search(query: str) -> str:
            """Search the internet for current and real-time information.
            
            Use this when the query involves:
            - Current events or recent news
            - Real-time data (stock prices, weather, sports scores)
            - Information that changes frequently
            - Factual verification of recent claims
            """

            return search.run(query)
        
        return [internet_search]
    
           
    def _create_agent(self, temperature: float):
        """Create ReAct agent with search capabilities"""
        
        chat_model = self.get_huggingface_model(temperature)
        agent = create_agent(model=chat_model, tools=self.search_tools)

        return agent
    
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
            streaming=True,
            do_sample=True
        )

        return ChatHuggingFace(llm=llm)

    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create session history for conversation management"""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]       
    
    # Needed for local model for streaming
    def _get_streaming_response(self, full_prompt: str, temperature: float, session_id: str):
        """Internal streaming response method (not cached)"""
        chat_model = self.get_model(temperature)
        chat_with_history = RunnableWithMessageHistory(chat_model, self.get_session_history)
        
        # Use stream for streaming responses
        return chat_with_history.stream(
            input=full_prompt,
            config={"configurable": {"session_id": session_id}}
        )

    # Needed for hugging face model for streaming
    def _get_huggingface_streaming_response(self, full_prompt: str, temperature: float, session_id: str):
        """Internal streaming response method (not cached)"""
        chat_model = self.get_huggingface_model(temperature)
        chat_with_history = RunnableWithMessageHistory(chat_model, self.get_session_history)
        
        # Use stream for streaming responses
        return chat_with_history.stream(
            input=full_prompt,
            config={"configurable": {"session_id": session_id}}
        )
    
    def _get_huggingface_streaming_response_with_search(self, full_prompt: str, temperature: float, session_id: str):
        """Internal streaming response with search tools (HuggingFace)"""
        
        # Get unwrapped agent
        if not self.agent_executor:
            self.agent_executor = self._create_agent(temperature)
        
        agent_with_history = RunnableWithMessageHistory(
            self.agent_executor,
            self.get_session_history,
            input_messages_key="messages",
            history_messages_key="history"
        )
    
        return agent_with_history.stream(
            {
                "messages": [{"role": "user", "content": full_prompt}]
            },
            config={"configurable": {"session_id": session_id}}
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
                request.temperature,
                request.session_id
            )

            # Yield each chunk from the stream
            for chunk in stream:
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
                    
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def get_response_with_search(self, request: ChatRequest):
        """
        Generate streaming AI responses with internet search capabilities.
        Returns generator that yields response chunks.
        Agent autonomously decides when to use search tools.
        
        This method follows the same streaming pattern as get_response_stream()
        but uses LangChain agents with search tools instead of direct LLM calls.
        """
        if not request.user_input:
            yield "Please provide input for the chatbot."
            return
        
        search_started = False
        
        try:
            # Create full prompt using prompt service
            full_prompt = PromptService.create_prompt_search(
                request.user_input,
                request.response_type,
                self.chatbot_name
            )
            
            print("DEBUG: Full prompt created for agent with search.")
            # Get streaming response (no caching for streams)
            stream = self._get_huggingface_streaming_response_with_search(
                full_prompt, 
                request.temperature,
                request.session_id
            )

            print("DEBUG: Starting to stream response with search...")
            # Yield each chunk from the stream
            for chunk in stream:
                content = None
                message_chunk = chunk
                # Format 1: Dict with 'model' key (agent format)
                if isinstance(chunk, dict) and 'model' in chunk:
                    messages = chunk.get('model', {}).get('messages', [])
                    if messages and hasattr(messages[0], 'content'):
                        content = messages[0].content
                    # Show search indicator when tools are called
                    if hasattr(message_chunk, 'tool_calls') and message_chunk.tool_calls and not search_started:
                        yield "\n\n🔍 *Searching the web...1*\n\n"
                        search_started = True
                
                # Format 2: Dict with 'messages' key
                elif isinstance(chunk, dict) and 'messages' in chunk:
                    messages = chunk.get('messages', [])
                    if messages and hasattr(messages[0], 'content'):
                        content = messages[0].content
                
                     # Show search indicator when tools are called
                    if hasattr(message_chunk, 'tool_calls') and message_chunk.tool_calls and not search_started:
                        yield "\n\n🔍 *Searching the web...2*\n\n"
                        search_started = True

                # Format 3: Direct message object
                elif hasattr(chunk, 'content'):
                    content = chunk.content
                
                # Format 4: String
                elif isinstance(chunk, str):
                    content = chunk
                
                if content:
                    yield content
                    
        except Exception as e:
            yield f"Error generating response with search: {str(e)}"

class PromptService:
    """Service for handling prompt generation and formatting"""
    
    # Add the internet search system prompt constant
    INTERNET_SEARCH_SYSTEM_PROMPT = """You are an intelligent AI assistant with access to real-time internet search capabilities to provide current and accurate information.

## Your Capabilities
- Your knowledge cutoff is from your training data, which may be outdated
- You have access to internet search tools to retrieve current, real-world information
- You can search the web, fetch webpage content, and synthesize information from multiple sources
- You should ALWAYS use internet search when the query involves:
  * Current events, news, or recent developments
  * Real-time data (stock prices, weather, sports scores, etc.)
  * Information that changes frequently (regulations, company financials, product releases)
  * Factual verification of recent claims
  * Any query explicitly asking for "latest", "current", "recent", or "today's" information
  * Technical documentation or API updates
  * Market data, business metrics, or economic indicators

## Decision Framework
Before answering, ask yourself:
1. Does this query require information newer than my training cutoff?
2. Could the answer have changed since my training data?
3. Is this asking for real-time or frequently-updated information?
4. Would current sources provide more accurate or complete information?

If YES to any question → Use internet search tools
If NO to all questions → Use your existing knowledge

## Search Strategy
When using internet search:
- Break complex queries into focused search terms
- Use multiple searches for comprehensive coverage
- Prioritize authoritative and recent sources
- Cross-reference information across multiple sources
- Always cite sources with inline references
- Verify information accuracy before presenting

## Response Format
- Lead with the most relevant, current information
- Cite all sources clearly
- Use clear formatting with headers and structure for complex answers
- Be explicit when information comes from real-time search vs. your training data
- If search fails or returns insufficient results, acknowledge limitations"""

    @staticmethod
    def create_prompt_search(user_input: str, response_type: str, chatbot_name: str) -> str:
        """Creates prompt for agent-based chatbot with search capabilities"""
        
        if not user_input:
            return None
        
        # Base system prompt with search capabilities
        system_prompt = PromptService.INTERNET_SEARCH_SYSTEM_PROMPT
        
        # Add personality based on response type
        if response_type == "creative":
            system_prompt += f"\n\nYou are {chatbot_name}, an imaginative AI assistant. Be creative and think outside the box while responding."
        elif response_type == "factual":
            system_prompt += f"\n\nYou are {chatbot_name}, a precise AI assistant. Stick to verified facts only. Always use search tools to verify recent information."
        else:
            system_prompt += f"\n\nYou are {chatbot_name}, a helpful AI assistant."
        
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