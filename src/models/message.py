"""
Message data model.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = None
    id: int = None

    def __post_init__(self) -> None:
        """Set default values after initialization."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """
        Convert message to dictionary format.

        Returns:
            Dictionary representation of the message.
        """
        return {
            "role": self.role,
            "content": self.content,
        }
