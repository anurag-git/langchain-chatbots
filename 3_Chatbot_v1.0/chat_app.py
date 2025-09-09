import streamlit as st
from ai_service import AIService, PromptService

class ChatApp:
    """Frontend application for chat interface"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.prompt_service = PromptService()
        
    def initialize_session_state(self):
        """Initializes required session state variables if they don't exist."""
        
        # Initialize chat history if it doesn't exist in session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Initialize temperature change tracker in session state
        if 'temp_changed' not in st.session_state:
            st.session_state.temp_changed = False
        
        if "use_chat_history" not in st.session_state:
            st.session_state.use_chat_history = True
        
        # Initialize the session state variable if it doesn't exist
        if 'num_chat_messages' not in st.session_state:
            st.session_state.num_chat_messages = 0
    
    def on_temp_change(self):
        """Mark that temperature has been changed to trigger response regeneration"""
        st.session_state.temp_changed = True
    
    def setup_page_config(self):
        """Set up the webpage layout and configuration"""
        st.set_page_config(
            page_title="Generative AI Chatbot",
            layout="wide"
        )
        st.title("Generative AI Chatbot using LLama and Streamlit")
    
    def render_controls(self):
        """Render user interface controls"""
        
        # Temperature slider
        temperature_param = st.slider(
            "Model temperature:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.01,
            help="Controls randomness: 0 = deterministic, 1 = very creative",
            on_change=self.on_temp_change,
            key="temperature"
        )
        
        # Response type selector
        res_type = st.selectbox(
            "Select response type:",
            ("standard", "creative", "factual"),
            index=0,
            help="Choose the type of response you want from the AI"
        )
        
        return temperature_param, res_type
    
    def display_chat_history(self):
        """Display existing chat messages"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    def process_user_input(self, user_prompt: str, temperature: float, response_type: str):
        """Process user input and generate AI response"""
        
        # Save user's message to chat history
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_prompt)
        
        # Show loading spinner while generating response
        with st.spinner("Generating response..."):
            # Create prompt
            full_prompt = self.prompt_service.create_prompt(
                user_prompt, 
                response_type
            )
            
            # Get AI response
            response = self.ai_service.get_response(full_prompt, temperature)
            
            # Save AI's response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.content
            })
            
            # Display AI response
            with st.chat_message("assistant"):
                st.write(response.content)
        
        # Add visual separator
        st.divider()
    
    def run(self):
        """Main application logic"""
        
        # Setup page configuration
        self.setup_page_config()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Render UI controls
        temperature_param, res_type = self.render_controls()
        
        # Display existing chat history
        self.display_chat_history()
        
        # Handle user input
        if user_prompt := st.chat_input("Enter your prompt:"):
            self.process_user_input(user_prompt, temperature_param, res_type)


# Main entry point
def main():
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
