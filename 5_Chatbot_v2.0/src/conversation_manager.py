"""
Conversation state management independent of UI framework
"""
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConversationMessage:
    """Single message in conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationManager:
    """Manages conversation state and history"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.messages: List[ConversationMessage] = []
        self.response_type = "standard"
        
    def add_user_message(self, content: str) -> None:
        """Add user message to conversation"""
        message = ConversationMessage(
            role="user",
            content=content,
            metadata={"response_type": self.response_type}
        )
        self.messages.append(message)
        
    def add_assistant_message(self, content: str, metadata: Dict[str, Any] = None) -> None:
        """Add assistant message to conversation"""
        message = ConversationMessage(
            role="assistant",
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history in format suitable for UI"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self.messages
        ]
        
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.messages.clear()
        
    def set_response_type(self, response_type: str) -> None:
        """Set response type for future messages"""
        self.response_type = response_type