"""
Conversation data model.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
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
    system_prompt: Optional[str] = None
    model_parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set default values after initialization."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

        # Set default model parameters if not provided
        if not self.model_parameters:
            self.model_parameters = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 2048,
            }

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
        Includes system prompt if available.

        Returns:
            List of message dictionaries.
        """
        history = []

        # Add system prompt if set
        if self.system_prompt:
            history.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add conversation messages
        history.extend([msg.to_dict() for msg in self.messages])

        return history
