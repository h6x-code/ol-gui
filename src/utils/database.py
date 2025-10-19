"""
SQLite database helper for conversation storage.
"""
import sqlite3
from pathlib import Path
from typing import Optional
from utils.config import DATABASE_FILE


class Database:
    """SQLite database helper for managing conversations and messages."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize the database connection.

        Args:
            db_path: Path to the database file. Defaults to DATABASE_FILE.
        """
        self.db_path = db_path or DATABASE_FILE
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Create database directory and initialize schema if needed."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_messages
                ON messages(conversation_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_updated
                ON conversations(updated_at DESC)
            """)

            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection object.
        """
        return sqlite3.connect(self.db_path)
