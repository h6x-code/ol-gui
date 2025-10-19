"""
Individual message bubble widget.
"""
import customtkinter as ctk
from typing import Literal


class MessageBubble(ctk.CTkFrame):
    """Widget for displaying a single message in the chat."""

    def __init__(
        self,
        parent,
        role: Literal["user", "assistant", "system"],
        content: str,
        **kwargs,
    ):
        """
        Initialize a message bubble.

        Args:
            parent: Parent widget.
            role: Message role (user, assistant, or system).
            content: Message content text.
            **kwargs: Additional arguments for CTkFrame.
        """
        super().__init__(parent, **kwargs)

        self.role = role
        self.content = content

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the message bubble UI."""
        # Configure frame
        if self.role == "user":
            fg_color = "#4a9eff"  # Primary blue for user
            text_color = "#ffffff"
            anchor = "e"  # Right align
        elif self.role == "assistant":
            fg_color = "#2d2d2d"  # Surface color for assistant
            text_color = "#e0e0e0"
            anchor = "w"  # Left align
        else:  # system
            fg_color = "#3d3d3d"
            text_color = "#fff066"
            anchor = "w"

        self.configure(fg_color=fg_color, corner_radius=10)

        # Role label (small text above message)
        role_label = ctk.CTkLabel(
            self,
            text=self.role.capitalize(),
            font=("", 11),
            text_color=text_color if self.role != "user" else "#b0d4ff",
            anchor=anchor,
        )
        role_label.pack(pady=(8, 2), padx=12, anchor=anchor, fill="x")

        # Message content
        content_label = ctk.CTkTextbox(
            self,
            font=("", 14),
            fg_color=fg_color,
            text_color=text_color,
            wrap="word",
            activate_scrollbars=False,
        )
        content_label.insert("1.0", self.content)
        content_label.configure(state="disabled")  # Read-only

        # Calculate height based on content
        num_lines = self.content.count("\n") + 1
        # Estimate line wrapping (rough approximation)
        chars_per_line = 60
        estimated_lines = max(num_lines, len(self.content) // chars_per_line + 1)
        height = min(max(estimated_lines * 20, 40), 400)  # Between 40 and 400px

        content_label.pack(pady=(0, 8), padx=12, fill="both", expand=True)
        content_label.configure(height=height)

    def update_content(self, content: str) -> None:
        """
        Update the message content (for streaming responses).

        Args:
            content: New content text.
        """
        self.content = content
        # Find and update the textbox
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkTextbox):
                widget.configure(state="normal")
                widget.delete("1.0", "end")
                widget.insert("1.0", content)
                widget.configure(state="disabled")

                # Update height
                num_lines = content.count("\n") + 1
                chars_per_line = 60
                estimated_lines = max(num_lines, len(content) // chars_per_line + 1)
                height = min(max(estimated_lines * 20, 40), 400)
                widget.configure(height=height)
                break
