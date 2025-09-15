import streamlit as st
from streamlit_option_menu import option_menu

from ai_service import AIService, PromptService

class ChatApp:
    """Frontend application for chat interface"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.prompt_service = PromptService()
        self.chatbot_name = "ChatBotX"
        
    def initialize_session_state(self):
        """Initializes required session state variables if they don't exist."""
        
        # Initialize chat history if it doesn't exist in session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
                
        # --- Initialize session state ---
        if "res_type" not in st.session_state:
            st.session_state["res_type"] = "standard"
       
    def setup_page_config(self):
        """Set up the webpage layout and configuration"""
        st.set_page_config(
            page_title="Generative AI Chatbot",
            layout="wide"
        )
        st.title("Generative AI Chatbot using LLama and Streamlit")
    
    def render_controls(self):
        """Render user interface controls"""
        
        # --- Global Response Type Selector (Top Pills) ---
        res_type_display = option_menu(
            None,
            ["💬 Standard", "✨ Creative", "📊 Factual"],
            icons=["chat", "stars", "bar-chart"],
            default_index=["standard", "creative", "factual"].index(st.session_state["res_type"]),
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
            }
        )

        # Map pill label → clean value
        res_type_map = {
            "💬 Standard": "standard",
            "✨ Creative": "creative",
            "📊 Factual": "factual",
        }

        st.session_state["res_type"] = res_type_map[res_type_display]

        st.write(f"🌍 Global Mode: **{st.session_state['res_type'].capitalize()}**")

        # --- Inline Per-Message Selector (Pills) ---
        inline_mode = option_menu(
            None,
            ["Use Global", "💬 Standard", "✨ Creative", "📊 Factual"],
            icons=["globe", "chat", "stars", "bar-chart"],
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#f9f9f9"},
                "icon": {"color": "black", "font-size": "16px"}, 
                "nav-link": {"font-size": "14px", "margin": "0px"},
                "nav-link-selected": {"background-color": "#2196F3", "color": "white"},
            }
        )

        # Decide final response type
        if inline_mode == "Use Global":
            res_mode = st.session_state["res_type"]
        else:
            res_mode = inline_mode
        
        print(f"Selected Response Mode: {res_mode}")
        print(f"Selected inline Mode: {inline_mode}")

        return res_mode
    
    def display_chat_history(self):
        """Display existing chat messages"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def process_user_input(self, user_prompt: str, response_type: str):
        """Process user input and generate AI response"""
        
        # Save user's message to chat history
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"**You:** {user_prompt}")
        

        # Show loading spinner while generating response
        with st.spinner("Generating response..."):
            # Create prompt
            full_prompt = self.prompt_service.create_prompt(
                user_prompt, 
                response_type,
                self.chatbot_name
            )

            # Pick temperature dynamically
            if st.session_state["res_type"] == "factual":
                temperature = 0.3
            elif st.session_state["res_type"] == "creative":
                temperature = 1.0
            else:
                temperature = 0.7
            
            # Get AI response
            response = self.ai_service.get_response(full_prompt, temperature)
            ai_message = response.content
            
            # Save AI's response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "name": self.chatbot_name,
                "content": ai_message
            })
            
            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(f"**{self.chatbot_name}:** {ai_message}")
        
        # Add visual separator
        st.divider()
    
    def run(self):
        """Main application logic"""
        
        # Setup page configuration
        self.setup_page_config()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Render UI controls
        res_mode = self.render_controls()
        
        # Display existing chat history
        self.display_chat_history()
        
        # Handle user input
        if user_prompt := st.chat_input("💭 Ask anything"):
            self.process_user_input(user_prompt, res_mode)


# Main entry point
def main():
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
