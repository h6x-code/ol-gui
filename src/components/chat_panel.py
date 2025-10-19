"""
Chat display panel component.
"""
import customtkinter as ctk
from typing import List, Optional
from components.message_bubble import MessageBubble
from models.message import Message


class ChatPanel(ctk.CTkScrollableFrame):
    """Scrollable panel for displaying chat messages."""

    def __init__(self, parent, **kwargs):
        """
        Initialize the chat panel.

        Args:
            parent: Parent widget.
            **kwargs: Additional arguments for CTkScrollableFrame.
        """
        super().__init__(parent, **kwargs)

        self.message_widgets: List[MessageBubble] = []
        self._current_streaming_bubble: Optional[MessageBubble] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the chat panel UI."""
        self.configure(
            fg_color="#1a1a1a",
            corner_radius=0,
        )

        # Welcome message
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Display a welcome message when chat is empty."""
        welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        welcome_frame.pack(expand=True, pady=100)

        title = ctk.CTkLabel(
            welcome_frame,
            text="Ol-GUI",
            font=("", 32, "bold"),
            text_color="#4a9eff",
        )
        title.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Start a conversation with your local LLM",
            font=("", 14),
            text_color="#a0a0a0",
        )
        subtitle.pack()

    def add_message(self, message: Message) -> MessageBubble:
        """
        Add a message to the chat panel.

        Args:
            message: Message object to display.

        Returns:
            The created MessageBubble widget.
        """
        # Remove welcome message if this is the first message
        if len(self.message_widgets) == 0:
            for widget in self.winfo_children():
                widget.destroy()

        # Create message bubble
        bubble = MessageBubble(
            self,
            role=message.role,
            content=message.content,
        )

        # Pack with appropriate alignment
        if message.role == "user":
            bubble.pack(
                pady=8,
                padx=(100, 20),
                anchor="e",
                fill="x",
            )
        else:  # assistant or system
            bubble.pack(
                pady=8,
                padx=(20, 100),
                anchor="w",
                fill="x",
            )

        self.message_widgets.append(bubble)

        # Scroll to bottom
        self.after(100, self._scroll_to_bottom)

        return bubble

    def start_streaming_message(self, role: str) -> MessageBubble:
        """
        Start a streaming message (initially empty).

        Args:
            role: Message role (usually 'assistant').

        Returns:
            The MessageBubble widget for updating.
        """
        message = Message(role=role, content="")
        bubble = self.add_message(message)
        self._current_streaming_bubble = bubble
        return bubble

    def update_streaming_message(self, content: str) -> None:
        """
        Update the current streaming message.

        Args:
            content: Updated content text.
        """
        if self._current_streaming_bubble:
            self._current_streaming_bubble.update_content(content)
            self.after(50, self._scroll_to_bottom)

    def finish_streaming_message(self) -> None:
        """Mark the streaming message as complete."""
        self._current_streaming_bubble = None

    def clear_messages(self) -> None:
        """Clear all messages from the chat panel."""
        for widget in self.message_widgets:
            widget.destroy()

        self.message_widgets.clear()
        self._current_streaming_bubble = None

        # Show welcome message again
        self._show_welcome_message()

    def load_messages(self, messages: List[Message]) -> None:
        """
        Load a list of messages into the chat panel.

        Args:
            messages: List of Message objects to display.
        """
        self.clear_messages()

        for message in messages:
            self.add_message(message)

    def _scroll_to_bottom(self) -> None:
        """Scroll the chat panel to the bottom."""
        # This is a workaround for CTkScrollableFrame
        self._parent_canvas.yview_moveto(1.0)
