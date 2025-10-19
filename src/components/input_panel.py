"""
Message input panel component.
"""
import customtkinter as ctk
from typing import Callable, Optional


class InputPanel(ctk.CTkFrame):
    """Panel for message input with send button."""

    def __init__(
        self,
        parent,
        on_send: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        """
        Initialize the input panel.

        Args:
            parent: Parent widget.
            on_send: Callback function when message is sent.
            **kwargs: Additional arguments for CTkFrame.
        """
        super().__init__(parent, **kwargs)

        self.on_send = on_send
        self._is_sending = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the input panel UI."""
        self.configure(
            fg_color="#2d2d2d",
            corner_radius=0,
            height=120,
        )

        # Create inner frame for padding
        inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Text input area
        self.input_text = ctk.CTkTextbox(
            inner_frame,
            font=("", 14),
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#4a9eff",
            wrap="word",
            height=60,
        )
        self.input_text.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.input_text.bind("<Return>", self._on_enter_key)
        self.input_text.bind("<Shift-Return>", self._on_shift_enter)

        # Bind focus event to show placeholder behavior
        self._setup_placeholder()

        # Button frame (vertical stack)
        button_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        button_frame.pack(side="right", fill="y")

        # Send button
        self.send_button = ctk.CTkButton(
            button_frame,
            text="Send",
            command=self._handle_send,
            font=("", 14, "bold"),
            fg_color="#4a9eff",
            hover_color="#3d8ee6",
            width=100,
            height=40,
        )
        self.send_button.pack(pady=(0, 5))

        # Stop button (hidden by default)
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self._handle_stop,
            font=("", 14),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100,
            height=40,
        )
        # Don't pack yet - will show when generating

    def _setup_placeholder(self) -> None:
        """Set up placeholder text behavior."""
        placeholder = "Type your message... (Shift+Enter for new line)"
        self.input_text.insert("1.0", placeholder)
        self.input_text.configure(text_color="#666666")

        def on_focus_in(event):
            if self.input_text.get("1.0", "end-1c") == placeholder:
                self.input_text.delete("1.0", "end")
                self.input_text.configure(text_color="#e0e0e0")

        def on_focus_out(event):
            if not self.input_text.get("1.0", "end-1c").strip():
                self.input_text.insert("1.0", placeholder)
                self.input_text.configure(text_color="#666666")

        self.input_text.bind("<FocusIn>", on_focus_in)
        self.input_text.bind("<FocusOut>", on_focus_out)

    def _on_enter_key(self, event) -> str:
        """
        Handle Enter key press.

        Args:
            event: Key event.

        Returns:
            "break" to prevent default behavior.
        """
        self._handle_send()
        return "break"  # Prevent newline

    def _on_shift_enter(self, event) -> None:
        """
        Handle Shift+Enter key press.

        Args:
            event: Key event.
        """
        # Allow default behavior (insert newline)
        pass

    def _handle_send(self) -> None:
        """Handle send button click or Enter key."""
        message = self.get_message()

        if message.strip() and self.on_send and not self._is_sending:
            self.on_send(message)
            self.clear_input()

    def _handle_stop(self) -> None:
        """Handle stop button click."""
        # This will be connected to the app's stop generation function
        if hasattr(self, "on_stop") and self.on_stop:
            self.on_stop()

    def get_message(self) -> str:
        """
        Get the current input text.

        Returns:
            The input text content.
        """
        text = self.input_text.get("1.0", "end-1c")
        placeholder = "Type your message... (Shift+Enter for new line)"

        if text == placeholder:
            return ""

        return text

    def clear_input(self) -> None:
        """Clear the input text area."""
        self.input_text.delete("1.0", "end")

    def set_sending_state(self, is_sending: bool) -> None:
        """
        Set the UI state for sending/generating.

        Args:
            is_sending: Whether currently sending/generating.
        """
        self._is_sending = is_sending

        if is_sending:
            self.send_button.pack_forget()
            self.stop_button.pack(pady=(0, 5))
            self.input_text.configure(state="disabled")
        else:
            self.stop_button.pack_forget()
            self.send_button.pack(pady=(0, 5))
            self.input_text.configure(state="normal")

    def set_send_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set the callback for sending messages.

        Args:
            callback: Function to call with message text.
        """
        self.on_send = callback

    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        """
        Set the callback for stopping generation.

        Args:
            callback: Function to call when stop is clicked.
        """
        self.on_stop = callback

    def focus_input(self) -> None:
        """Set focus to the input text area."""
        self.input_text.focus()
