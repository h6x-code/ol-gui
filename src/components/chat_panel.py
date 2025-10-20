"""
Chat display panel component.
"""
import customtkinter as ctk
from typing import List, Optional
from components.message_bubble import MessageBubble
from models.message import Message


class ChatPanel(ctk.CTkScrollableFrame):
    """Scrollable panel for displaying chat messages."""

    def __init__(self, parent, font_size: int = 14, **kwargs):
        """
        Initialize the chat panel.

        Args:
            parent: Parent widget.
            font_size: Default font size for messages.
            **kwargs: Additional arguments for CTkScrollableFrame.
        """
        super().__init__(parent, **kwargs)

        self.message_widgets: List[MessageBubble] = []
        self._current_streaming_bubble: Optional[MessageBubble] = None
        self.font_size = font_size
        self._welcome_frame: Optional[ctk.CTkFrame] = None

        self._setup_ui()

        # Bind to configure event to resize message bubbles
        self.bind("<Configure>", self._on_resize)

        # Bind mouse wheel scrolling
        self._bind_mouse_wheel()

    def _setup_ui(self) -> None:
        """Set up the chat panel UI."""
        self.configure(
            fg_color=("#ffffff", "#1a1a1a"),  # (light, dark)
            corner_radius=0,
        )

        # Welcome message
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Display a welcome message when chat is empty."""
        # Only create welcome message if it doesn't already exist
        if self._welcome_frame is not None and self._welcome_frame.winfo_exists():
            return

        self._welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._welcome_frame.pack(expand=True, pady=100)

        title = ctk.CTkLabel(
            self._welcome_frame,
            text="Ol-GUI",
            font=("", 48, "bold"),
            text_color=("#2196f3", "#4a9eff"),  # (light, dark)
        )
        title.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            self._welcome_frame,
            text="Start a conversation with your local LLM",
            font=("", 24),
            text_color=("#666666", "#a0a0a0"),  # (light, dark)
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
            if self._welcome_frame is not None and self._welcome_frame.winfo_exists():
                self._welcome_frame.destroy()
                self._welcome_frame = None

        # Create message bubble with current font size
        bubble = MessageBubble(
            self,
            role=message.role,
            content=message.content,
            font_size=self.font_size,
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

        # Force update of the scrollable frame's canvas
        self.update_idletasks()
        if hasattr(self, '_parent_canvas'):
            self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))

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
            # Update canvas scroll region as content grows
            self.update_idletasks()
            if hasattr(self, '_parent_canvas'):
                self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
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
        # Access the internal canvas and scroll to bottom
        try:
            # CTkScrollableFrame has an internal canvas widget
            if hasattr(self, '_parent_canvas'):
                self._parent_canvas.yview_moveto(1.0)
            # Force update to ensure scrolling works
            self.update_idletasks()
        except Exception as e:
            print(f"Scroll error: {e}")

    def update_theme(self, theme: str) -> None:
        """
        Update the chat panel theme colors.

        Args:
            theme: Theme name ("dark", "light", or "system")
        """
        if theme == "light":
            bg_color = "#ffffff"
        else:
            bg_color = "#1a1a1a"

        self.configure(fg_color=bg_color)

    def _on_resize(self, event) -> None:
        """Handle resize events to recalculate all message bubble heights."""
        # Only recalculate if the width actually changed
        if event.widget == self and event.width != getattr(self, '_last_width', 0):
            self._last_width = event.width
            # Debounce resize events to avoid too many updates
            if hasattr(self, '_resize_timer'):
                self.after_cancel(self._resize_timer)
            self._resize_timer = self.after(100, self._recalculate_all_heights)

    def _recalculate_all_heights(self) -> None:
        """Recalculate heights for all message bubbles."""
        for bubble in self.message_widgets:
            if hasattr(bubble, '_calculate_height'):
                bubble._calculate_height()

    def _bind_mouse_wheel(self) -> None:
        """Bind mouse wheel events for scrolling when mouse enters this widget."""
        # Bind mouse wheel only when mouse is over this widget
        self.bind("<Enter>", self._on_mouse_enter)
        self.bind("<Leave>", self._on_mouse_leave)

    def _on_mouse_enter(self, event) -> None:
        """Enable mouse wheel scrolling when mouse enters the chat panel."""
        if hasattr(self, '_parent_canvas'):
            # Linux scroll (Button-4/5)
            self._parent_canvas.bind_all("<Button-4>", self._on_mouse_wheel)
            self._parent_canvas.bind_all("<Button-5>", self._on_mouse_wheel)

    def _on_mouse_leave(self, event) -> None:
        """Disable mouse wheel scrolling when mouse leaves the chat panel."""
        if hasattr(self, '_parent_canvas'):
            # Unbind mouse wheel events
            self._parent_canvas.unbind_all("<Button-4>")
            self._parent_canvas.unbind_all("<Button-5>")

    def _on_mouse_wheel(self, event) -> None:
        """
        Handle mouse wheel scrolling.

        Args:
            event: Mouse wheel event.
        """
        if hasattr(self, '_parent_canvas'):
            # Linux uses Button-4 (scroll up) and Button-5 (scroll down)
            if event.num == 4:
                self._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._parent_canvas.yview_scroll(1, "units")
            # Windows/Mac use event.delta
            elif hasattr(event, 'delta'):
                self._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
