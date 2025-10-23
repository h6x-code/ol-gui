"""
Conversation management service.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import json

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

    def create_conversation(
        self,
        title: str,
        model: str,
        system_prompt: Optional[str] = None,
        model_parameters: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            title: The conversation title.
            model: The model name to use.
            system_prompt: Optional system prompt for the conversation.
            model_parameters: Optional model parameters (temperature, top_p, etc.).

        Returns:
            The created conversation.
        """
        # Use default parameters if not provided
        if model_parameters is None:
            model_parameters = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 2048,
            }

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO conversations
                   (title, model, system_prompt, model_parameters)
                   VALUES (?, ?, ?, ?)""",
                (title, model, system_prompt, json.dumps(model_parameters)),
            )
            conn.commit()
            conversation_id = cursor.lastrowid

        return Conversation(
            id=conversation_id,
            title=title,
            model=model,
            system_prompt=system_prompt,
            model_parameters=model_parameters,
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

        # Parse model parameters from JSON
        model_parameters = {}
        if row["model_parameters"]:
            try:
                model_parameters = json.loads(row["model_parameters"])
            except json.JSONDecodeError:
                # Use defaults if JSON is invalid
                model_parameters = {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_tokens": 2048,
                }

        return Conversation(
            id=row["id"],
            title=row["title"],
            model=row["model"],
            messages=messages,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            system_prompt=row["system_prompt"],
            model_parameters=model_parameters,
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

        conversations = []
        for row in rows:
            # Parse model parameters from JSON
            model_parameters = {}
            if row["model_parameters"]:
                try:
                    model_parameters = json.loads(row["model_parameters"])
                except json.JSONDecodeError:
                    model_parameters = {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_tokens": 2048,
                    }

            conversations.append(
                Conversation(
                    id=row["id"],
                    title=row["title"],
                    model=row["model"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    system_prompt=row["system_prompt"],
                    model_parameters=model_parameters,
                )
            )

        return conversations

    def rename_conversation(self, conversation_id: int, new_title: str) -> None:
        """
        Rename a conversation.

        Args:
            conversation_id: The conversation ID to rename.
            new_title: The new title for the conversation.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_title, conversation_id),
            )
            conn.commit()

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

    def update_system_prompt(self, conversation_id: int, system_prompt: Optional[str]) -> None:
        """
        Update the system prompt for a conversation.

        Args:
            conversation_id: The conversation ID.
            system_prompt: The new system prompt (or None to clear).
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET system_prompt = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (system_prompt, conversation_id),
            )
            conn.commit()

    def update_model_parameters(
        self, conversation_id: int, model_parameters: Dict[str, Any]
    ) -> None:
        """
        Update model parameters for a conversation.

        Args:
            conversation_id: The conversation ID.
            model_parameters: Dictionary of model parameters.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET model_parameters = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(model_parameters), conversation_id),
            )
            conn.commit()

    def search_messages(self, query: str, conversation_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query string.

        Args:
            query: Search query string.
            conversation_id: Optional conversation ID to limit search scope.

        Returns:
            List of dictionaries with message and conversation info.
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if conversation_id:
                # Search within a specific conversation
                cursor.execute(
                    """SELECT m.*, c.title as conversation_title
                       FROM messages m
                       JOIN conversations c ON m.conversation_id = c.id
                       WHERE m.conversation_id = ? AND m.content LIKE ?
                       ORDER BY m.created_at DESC""",
                    (conversation_id, f"%{query}%"),
                )
            else:
                # Search across all conversations
                cursor.execute(
                    """SELECT m.*, c.title as conversation_title
                       FROM messages m
                       JOIN conversations c ON m.conversation_id = c.id
                       WHERE m.content LIKE ?
                       ORDER BY m.created_at DESC""",
                    (f"%{query}%",),
                )

            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "conversation_title": row["conversation_title"],
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
