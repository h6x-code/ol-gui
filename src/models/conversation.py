"""
Conversation data model.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from models.message import Message


@dataclass
class Conversation:
    """Represents a conversation with message history."""

    title: str
    model: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Set default values after initialization."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def add_message(self, message: Message) -> None:
        """
        Add a message to the conversation.

        Args:
            message: The message to add.
        """
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_message_history(self) -> List[dict]:
        """
        Get message history in Ollama API format.

        Returns:
            List of message dictionaries.
        """
        return [msg.to_dict() for msg in self.messages]
