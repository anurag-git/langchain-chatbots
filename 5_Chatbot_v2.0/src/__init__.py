"""
Core source code package for the chatbot application.

This package contains the main business logic and AI service components.
"""
from .chatbot import ChatbotService, ChatRequest, ChatResponse, PromptService
from .conversation_manager import ConversationManager, ConversationMessage
from .nlp_utils import TextProcessor, IntentClassifier, EntityExtractor
from .api_utils import APIClient, ModelAPIAdapter, ExternalServiceIntegration

__version__ = "1.0.0"

__all__ = [
    # Core chatbot components
    'ChatbotService',
    'ChatRequest', 
    'ChatResponse',
    'PromptService',
    
    # Conversation management
    'ConversationManager',
    'ConversationMessage',
    
    # NLP utilities
    'TextProcessor',
    'IntentClassifier', 
    'EntityExtractor',
    
    # API utilities
    'APIClient',
    'ModelAPIAdapter',
    'ExternalServiceIntegration'
]

# Package metadata
__author__ = "Chatbot Development Team"
__email__ = "dev@chatbot.com"
__description__ = "Core AI chatbot service components"
