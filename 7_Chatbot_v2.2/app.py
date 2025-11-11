"""
Main Streamlit application entry point.
Orchestrates UI components and AI services with dependency injection.
Modified to support persistent database configuration for chat history.
"""
import streamlit as st
import yaml
from pathlib import Path
from src import ChatbotService, ConversationManager
from ui import PageConfigComponent, SidebarComponent, ChatInterface

def validate_config_structure(config: dict) -> None:
    """Validate that configuration contains all required keys"""
    required_keys = {
        'ai_model': ['name'],
        'chatbot': ['name'], 
        'ui': ['page_title', 'layout', 'app_title', 'app_message'],
        'cache': ['enabled'],
        'database': ['url']
    }
    
    for section, keys in required_keys.items():
        if section not in config:
            raise ValueError(f"Missing required section: '{section}'")
        
        for key in keys:
            if key not in config[section]:
                raise ValueError(f"Missing required key: '{key}' in section '{section}'")


def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = Path("config/settings.yaml")
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Please create settings.yaml with required configuration."
        )
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            
        # Validate required keys exist
        validate_config_structure(config)
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in configuration file: {e}")

def initialize_services(config: dict) -> tuple:
    """Initialize all services with dependency injection"""
    chatbot_service = ChatbotService(config)
    conversation_manager = ConversationManager()
    return chatbot_service, conversation_manager


def main():
    """Main application function"""
    # Load configuration
    config = load_config()
    
    # Initialize services
    chatbot_service, conversation_manager = initialize_services(config)
    
    # Initialize page configuration
    page_config = PageConfigComponent(config)
    page_config.render()
    
    # Create UI components
    chat_interface = ChatInterface(config, chatbot_service, conversation_manager)
    sidebar = SidebarComponent(config, conversation_manager)
    
    # Render sidebar and get settings
    res_type = sidebar.render()
    print(f"Selected response type: {res_type}")

    # Render main chat interface
    chat_interface.render(res_type)


if __name__ == "__main__":
    main()
