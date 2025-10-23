"""
Export service for conversation data.
"""
from typing import List, Optional
from datetime import datetime
import json
from pathlib import Path

from models.conversation import Conversation
from models.message import Message


class ExportService:
    """Service for exporting conversations to various formats."""

    @staticmethod
    def export_to_markdown(conversation: Conversation) -> str:
        """
        Export conversation to Markdown format.

        Args:
            conversation: Conversation to export.

        Returns:
            Markdown formatted string.
        """
        lines = []

        # Header
        lines.append(f"# {conversation.title}")
        lines.append("")
        lines.append(f"**Model:** {conversation.model}")
        lines.append(f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # System prompt if present
        if conversation.system_prompt:
            lines.append("")
            lines.append("## System Prompt")
            lines.append("")
            lines.append(f"> {conversation.system_prompt}")

        # Model parameters
        if conversation.model_parameters:
            lines.append("")
            lines.append("## Model Parameters")
            lines.append("")
            for key, value in conversation.model_parameters.items():
                lines.append(f"- **{key}:** {value}")

        # Messages
        lines.append("")
        lines.append("## Conversation")
        lines.append("")

        for msg in conversation.messages:
            role_title = msg.role.capitalize()
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else ""

            lines.append(f"### {role_title}")
            if timestamp:
                lines.append(f"*{timestamp}*")
            lines.append("")
            lines.append(msg.content)
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def export_to_json(conversation: Conversation) -> str:
        """
        Export conversation to JSON format.

        Args:
            conversation: Conversation to export.

        Returns:
            JSON formatted string.
        """
        data = {
            "id": conversation.id,
            "title": conversation.title,
            "model": conversation.model,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "system_prompt": conversation.system_prompt,
            "model_parameters": conversation.model_parameters,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in conversation.messages
            ],
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_text(conversation: Conversation) -> str:
        """
        Export conversation to plain text format.

        Args:
            conversation: Conversation to export.

        Returns:
            Plain text formatted string.
        """
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(conversation.title)
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Model: {conversation.model}")
        lines.append(f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # System prompt if present
        if conversation.system_prompt:
            lines.append("")
            lines.append("System Prompt:")
            lines.append("-" * 60)
            lines.append(conversation.system_prompt)
            lines.append("-" * 60)

        # Model parameters
        if conversation.model_parameters:
            lines.append("")
            lines.append("Model Parameters:")
            for key, value in conversation.model_parameters.items():
                lines.append(f"  {key}: {value}")

        # Messages
        lines.append("")
        lines.append("Conversation:")
        lines.append("=" * 60)

        for msg in conversation.messages:
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else ""

            lines.append("")
            lines.append(f"[{msg.role.upper()}] {timestamp}")
            lines.append("-" * 60)
            lines.append(msg.content)
            lines.append("-" * 60)

        return "\n".join(lines)

    @staticmethod
    def save_to_file(content: str, file_path: Path) -> None:
        """
        Save content to a file.

        Args:
            content: Content to save.
            file_path: Path to save the file.

        Raises:
            Exception: If file write fails.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")

    @staticmethod
    def export_conversation(
        conversation: Conversation,
        format_type: str,
        file_path: Optional[Path] = None
    ) -> str:
        """
        Export conversation in the specified format.

        Args:
            conversation: Conversation to export.
            format_type: Export format ('markdown', 'json', or 'text').
            file_path: Optional file path to save to. If None, returns content string.

        Returns:
            Exported content as string.

        Raises:
            ValueError: If format_type is invalid.
        """
        if format_type == "markdown":
            content = ExportService.export_to_markdown(conversation)
        elif format_type == "json":
            content = ExportService.export_to_json(conversation)
        elif format_type == "text":
            content = ExportService.export_to_text(conversation)
        else:
            raise ValueError(f"Invalid format type: {format_type}")

        if file_path:
            ExportService.save_to_file(content, file_path)

        return content

    @staticmethod
    def get_default_filename(conversation: Conversation, format_type: str) -> str:
        """
        Generate a default filename for the export.

        Args:
            conversation: Conversation to export.
            format_type: Export format type.

        Returns:
            Default filename string.
        """
        # Sanitize title for filename
        safe_title = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in conversation.title
        )
        safe_title = safe_title.strip()[:50]  # Limit length

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Determine extension
        extensions = {
            "markdown": "md",
            "json": "json",
            "text": "txt",
        }
        ext = extensions.get(format_type, "txt")

        return f"{safe_title}_{timestamp}.{ext}"
