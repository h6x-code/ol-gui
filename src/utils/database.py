"""
SQLite database helper for conversation storage.
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional
from utils.config import DATABASE_FILE


class Database:
    """SQLite database helper for managing conversations and messages."""

    CURRENT_SCHEMA_VERSION = 2  # Increment when schema changes

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize the database connection.

        Args:
            db_path: Path to the database file. Defaults to DATABASE_FILE.
        """
        self.db_path = db_path or DATABASE_FILE
        self._ensure_database_exists()
        self._migrate_schema()

    def _ensure_database_exists(self) -> None:
        """Create database directory and initialize schema if needed."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create conversations table with new fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    system_prompt TEXT,
                    model_parameters TEXT
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

            # Create schema version table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _migrate_schema(self) -> None:
        """Migrate database schema to current version."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get current schema version
            cursor.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            current_version = result[0] if result[0] is not None else 0

            # Migration from version 0 to 1: Add system_prompt and model_parameters
            if current_version < 1:
                self._migrate_to_v1(cursor)
                cursor.execute("INSERT INTO schema_version (version) VALUES (1)")

            # Migration from version 1 to 2: (Reserved for future use)
            if current_version < 2:
                # No changes yet, but version table is ready
                cursor.execute("INSERT INTO schema_version (version) VALUES (2)")

            conn.commit()

    def _migrate_to_v1(self, cursor: sqlite3.Cursor) -> None:
        """
        Migrate to schema version 1: Add system_prompt and model_parameters columns.

        Args:
            cursor: Database cursor.
        """
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add system_prompt column if it doesn't exist
        if "system_prompt" not in columns:
            cursor.execute("ALTER TABLE conversations ADD COLUMN system_prompt TEXT")

        # Add model_parameters column if it doesn't exist
        if "model_parameters" not in columns:
            cursor.execute("ALTER TABLE conversations ADD COLUMN model_parameters TEXT")

            # Set default parameters for existing conversations
            default_params = json.dumps({
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 2048,
            })
            cursor.execute(
                "UPDATE conversations SET model_parameters = ? WHERE model_parameters IS NULL",
                (default_params,)
            )

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection object.
        """
        return sqlite3.connect(self.db_path)
