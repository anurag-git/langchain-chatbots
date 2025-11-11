"""
User Interface package for the Streamlit-based chatbot application.

This package contains all UI components, styling, and presentation logic
separated from business logic and AI services.
"""
from .components import (
    UIComponent,
    PageConfigComponent, 
    SidebarComponent,
    ChatInterface,
    # ErrorDisplayComponent,
    # MetricsDisplayComponent,
    # SettingsPanel
)

__version__ = "1.0.0"

__all__ = [
    # Base UI component
    'UIComponent',
    
    # Main UI components
    'PageConfigComponent',
    'SidebarComponent', 
    'ChatInterface',
    
    # # Utility UI components
    # 'ErrorDisplayComponent',
    # 'MetricsDisplayComponent',
    # 'SettingsPanel'
]

# Package metadata
__author__ = "Chatbot UI Team"
__email__ = "ui-dev@chatbot.com"
__description__ = "Streamlit-based user interface components for AI chatbot"

# UI Configuration constants
DEFAULT_THEME = "light"
SUPPORTED_THEMES = ["light", "dark", "auto"]
DEFAULT_LAYOUT = "wide"
SUPPORTED_LAYOUTS = ["centered", "wide"]

# Component registration for dynamic loading
COMPONENT_REGISTRY = {
    "page_config": PageConfigComponent,
    "sidebar": SidebarComponent,
    "chat_interface": ChatInterface
    # "error_display": ErrorDisplayComponent,
    # "metrics_display": MetricsDisplayComponent,
    # "settings_panel": SettingsPanel
}

def get_component(component_name: str):
    """
    Get a UI component class by name
    
    Args:
        component_name: Name of the component to retrieve
        
    Returns:
        Component class if found, None otherwise
        
    Example:
        >>> ChatComponent = get_component("chat_interface")
        >>> chat = ChatComponent(service, manager)
    """
    return COMPONENT_REGISTRY.get(component_name.lower())

def list_components():
    """
    List all available UI components
    
    Returns:
        List of component names
        
    Example:
        >>> components = list_components()
        >>> print(components)
        ['page_config', 'sidebar', 'chat_interface', ...]
    """
    return list(COMPONENT_REGISTRY.keys())

def validate_theme(theme: str) -> bool:
    """
    Validate if theme is supported
    
    Args:
        theme: Theme name to validate
        
    Returns:
        True if theme is supported, False otherwise
    """
    return theme.lower() in SUPPORTED_THEMES

def validate_layout(layout: str) -> bool:
    """
    Validate if layout is supported
    
    Args:
        layout: Layout name to validate
        
    Returns:
        True if layout is supported, False otherwise
    """
    return layout.lower() in SUPPORTED_LAYOUTS

# UI utility functions
def apply_custom_css():
    """
    Apply custom CSS styling to the Streamlit app
    This function can be imported and used in the main app
    """
    import streamlit as st
    from pathlib import Path
    
    # Load custom CSS if it exists
    css_file = Path(__file__).parent / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    """
    Initialize common session state variables for UI components
    This ensures consistent state management across components
    """
    import streamlit as st
    
    # Initialize common UI state
    if 'ui_theme' not in st.session_state:
        st.session_state.ui_theme = DEFAULT_THEME
    
    if 'ui_layout' not in st.session_state:
        st.session_state.ui_layout = DEFAULT_LAYOUT
    
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True
    
    if 'show_debug_info' not in st.session_state:
        st.session_state.show_debug_info = False
    
    if 'ui_messages' not in st.session_state:
        st.session_state.ui_messages = []
    
    if 'ui_errors' not in st.session_state:
        st.session_state.ui_errors = []

# Component factory for dependency injection
def create_ui_components(chatbot_service, conversation_manager, config=None):
    """
    Factory function to create all UI components with proper dependencies
    
    Args:
        chatbot_service: AI chatbot service instance
        conversation_manager: Conversation management service
        config: Optional configuration dictionary
        
    Returns:
        Dictionary of initialized UI components
        
    Example:
        >>> components = create_ui_components(chatbot_service, conv_manager)
        >>> sidebar = components['sidebar']
        >>> chat_interface = components['chat_interface']
    """
    config = config or {}
    
    components = {
        'page_config': PageConfigComponent(config),
        'sidebar': SidebarComponent(chatbot_service, conversation_manager),
        'chat_interface': ChatInterface(chatbot_service, conversation_manager)
        # 'error_display': ErrorDisplayComponent(chatbot_service, conversation_manager),
        # 'metrics_display': MetricsDisplayComponent(chatbot_service, conversation_manager),
        # 'settings_panel': SettingsPanel(chatbot_service, conversation_manager)
    }
    
    return components

# Version compatibility check
def check_streamlit_version():
    """
    Check if the installed Streamlit version is compatible
    
    Returns:
        Tuple of (is_compatible: bool, current_version: str, required_version: str)
    """
    try:
        import streamlit as st
        from packaging import version
        
        current_version = st.__version__
        required_version = "1.25.0"
        
        is_compatible = version.parse(current_version) >= version.parse(required_version)
        
        return is_compatible, current_version, required_version
        
    except ImportError:
        return False, "Not installed", "1.25.0"

# Development utilities
def enable_debug_mode():
    """
    Enable debug mode for UI components
    Shows additional debug information and development tools
    """
    import streamlit as st
    st.session_state.show_debug_info = True

def disable_debug_mode():
    """
    Disable debug mode for UI components
    """
    import streamlit as st
    st.session_state.show_debug_info = False

def get_ui_state_summary():
    """
    Get summary of current UI state for debugging
    
    Returns:
        Dictionary with UI state information
    """
    import streamlit as st
    
    return {
        "theme": st.session_state.get('ui_theme', 'unknown'),
        "layout": st.session_state.get('ui_layout', 'unknown'),
        "sidebar_expanded": st.session_state.get('sidebar_expanded', False),
        "debug_mode": st.session_state.get('show_debug_info', False),
        "message_count": len(st.session_state.get('ui_messages', [])),
        "error_count": len(st.session_state.get('ui_errors', [])),
        "session_keys": list(st.session_state.keys())
    }
