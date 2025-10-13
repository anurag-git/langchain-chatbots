"""
Pure Streamlit UI components with no AI logic
"""
import streamlit as st
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict
from src import ChatbotService, ChatRequest
from src import ConversationManager


class UIComponent(ABC):
    """Base class for all UI components"""
    
    def __init__(self, chatbot_service: ChatbotService, conversation_manager: ConversationManager):
        self.chatbot_service = chatbot_service
        self.conversation_manager = conversation_manager
    
    @abstractmethod
    def render(self):
        """Render the component"""
        pass


class PageConfigComponent(UIComponent):
    """Handles page configuration setup"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        super().__init__(None, None)  # Page config doesn't need services
    
    def render(self):
        """Set up the webpage layout and configuration"""
        page_title = self.config['ui']['page_title']
        layout = self.config['ui']['layout']
        app_message = self.config['ui']['app_message']
        
        st.set_page_config(page_title=page_title, layout=layout)

        html_code = f"""
            <div style='display: flex; justify-content: center; align-items: center; height: 80vh;'>
                <h2>{app_message}</h2>
            </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)

class SidebarComponent(UIComponent):
    """Renders sidebar controls"""
    
    def __init__(self, config: Dict[str, Any], conversation_manager: ConversationManager):
        self.config = config
        self.conversation_manager = conversation_manager
        super().__init__(None, conversation_manager)

    def render(self):
        """Render enhanced sidebar with collapsible sections and controls"""

        app_title = self.config['ui']['app_title']
        with st.sidebar:
            # Logo/Header
            html_code = f"""
            <div style='text-align: center; padding: 1rem;'>
                <h2 style='color: #4CAF50; margin: 0;'>🤖</h2>
                <h3 style='margin: 0.5rem 0;'>{app_title}</h3>
            </div>
            """
            st.markdown(html_code, unsafe_allow_html=True)

            # Response type selector
            response_type = st.selectbox(
                "Response Style",
                options=["standard", "creative", "factual"],
                index=0,
                key="response_type"
            )
            self.conversation_manager.set_response_type(response_type)
                      
            temperature = 0.7  # Fixed temperature for simplicity

            # Clear conversation button
            if st.button("Clear Conversation", type="secondary"):
                self.conversation_manager.clear_conversation()
                if 'messages' in st.session_state:
                    st.session_state.messages = []
                st.rerun()
            
            return {
                "response_type": response_type,
                "temperature": temperature
            }


class ChatInterface(UIComponent):
    """Main chat interface component"""
    
    def render(self):
        """Render the main chat interface"""
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        self._display_chat_history()
        
        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            self._handle_user_input(prompt)
    
    def _display_chat_history(self):
        """Display conversation history"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def _handle_user_input(self, user_input: str):
        """Handle user input and generate response"""
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        self.conversation_manager.add_user_message(user_input)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # # Generate and display assistant response
        # with st.chat_message("assistant"):
        #     with st.spinner("Thinking..."):
        #         self._generate_and_display_response(user_input)
    
        # Generate and display assistant streaming response
        with st.chat_message("assistant"):
            self._generate_and_display_streaming_response(user_input)

    def _generate_and_display_response(self, user_input: str):
        """Generate response from AI service and display"""
        try:
            # Get current settings
            response_type = st.session_state.get("response_type", "standard")
            temperature = st.session_state.get("temperature", 0.7)
            
            # Create request
            request = ChatRequest(
                user_input=user_input,
                temperature=temperature,
                response_type=response_type,
                session_id=self.conversation_manager.session_id
            )
            
            # Get response (sync wrapper for async method)
            response = asyncio.run(self.chatbot_service.get_response(request))
            
            # Display response
            st.markdown(response.message)
            
            # Add to session state and conversation manager
            st.session_state.messages.append({"role": "assistant", "content": response.message})
            self.conversation_manager.add_assistant_message(response.message, response.metadata)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    def _generate_and_display_streaming_response(self, user_input: str):
        """Generate response from AI service and display with streaming"""
        try:
            # Get current settings
            response_type = st.session_state.get("response_type", "standard")
            temperature = st.session_state.get("temperature", 0.7)
            
            # Create request
            request = ChatRequest(
                user_input=user_input,
                temperature=temperature,
                response_type=response_type,
                session_id=self.conversation_manager.session_id
            )
            
            # Get streaming response using the new method
            response_generator = self.chatbot_service.get_response_stream(request)
            
            # Stream the response using st.write_stream
            response_content = st.write_stream(response_generator)
            
            # Add to session state and conversation manager
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            self.conversation_manager.add_assistant_message(response_content, {})
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
