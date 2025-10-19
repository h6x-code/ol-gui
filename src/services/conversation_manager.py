"""
Conversation management service.
"""
from typing import List, Optional
from datetime import datetime
import sqlite3

from models.conversation import Conversation
from models.message import Message
from utils.database import Database


class ConversationManager:
    """Service for managing conversations and message history."""

    def __init__(self, database: Optional[Database] = None) -> None:
        """
        Initialize the conversation manager.

        Args:
            database: Database instance. Creates new one if not provided.
        """
        self.db = database or Database()

    def create_conversation(self, title: str, model: str) -> Conversation:
        """
        Create a new conversation.

        Args:
            title: The conversation title.
            model: The model name to use.

        Returns:
            The created conversation.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (title, model) VALUES (?, ?)",
                (title, model),
            )
            conn.commit()
            conversation_id = cursor.lastrowid

        return Conversation(
            id=conversation_id,
            title=title,
            model=model,
        )

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """
        Get a conversation by ID with all messages.

        Args:
            conversation_id: The conversation ID.

        Returns:
            The conversation or None if not found.
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get conversation
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Get messages
            cursor.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,),
            )
            message_rows = cursor.fetchall()

        messages = [
            Message(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                created_at=datetime.fromisoformat(msg["created_at"]),
            )
            for msg in message_rows
        ]

        return Conversation(
            id=row["id"],
            title=row["title"],
            model=row["model"],
            messages=messages,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def add_message(
        self, conversation_id: int, role: str, content: str
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID.
            role: Message role ('user', 'assistant', 'system').
            content: Message content.

        Returns:
            The created message.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Insert message
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content),
            )

            # Update conversation timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )

            conn.commit()
            message_id = cursor.lastrowid

        return Message(
            id=message_id,
            role=role,
            content=content,
        )

    def list_conversations(self) -> List[Conversation]:
        """
        List all conversations ordered by updated_at.

        Returns:
            List of conversations (without messages loaded).
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()

        return [
            Conversation(
                id=row["id"],
                title=row["title"],
                model=row["model"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def delete_conversation(self, conversation_id: int) -> None:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID to delete.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM conversations WHERE id = ?", (conversation_id,)
            )
            conn.commit()
