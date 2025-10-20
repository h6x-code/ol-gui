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
        font_size: int = 14,
        **kwargs,
    ):
        """
        Initialize a message bubble.

        Args:
            parent: Parent widget.
            role: Message role (user, assistant, or system).
            content: Message content text.
            font_size: Font size for the message text (default: 14).
            **kwargs: Additional arguments for CTkFrame.
        """
        super().__init__(parent, **kwargs)

        self.role = role
        self.content = content
        self.font_size = font_size

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the message bubble UI."""
        # Configure frame with theme-aware colors
        if self.role == "user":
            fg_color = ("#2196f3", "#4a9eff")  # Primary blue for user (light, dark)
            text_color = ("#ffffff", "#ffffff")  # White text in both themes
            anchor = "e"  # Right align
        elif self.role == "assistant":
            fg_color = ("#f5f5f5", "#2d2d2d")  # Surface color for assistant (light, dark)
            text_color = ("#1a1a1a", "#e0e0e0")  # Text color (light, dark)
            anchor = "w"  # Left align
        else:  # system
            fg_color = ("#ffa33b", "#3d3d3d")  # Yellow/dark for system (light, dark)
            text_color = ("#1a1a1a", "#ffb96a")  # Text color (light, dark)
            anchor = "w"

        self.configure(fg_color=fg_color, corner_radius=10)

        # Role label (small text above message)
        label_color = text_color

        # Calculate role label font size (smaller than content)
        label_font_size = max(11, self.font_size - 3)

        role_label = ctk.CTkLabel(
            self,
            text=self.role.capitalize(),
            font=("", label_font_size),
            text_color=label_color,
            anchor=anchor,
        )
        role_label.pack(pady=(8, 2), padx=12, anchor=anchor, fill="x")

        # Message content
        content_label = ctk.CTkTextbox(
            self,
            font=("", self.font_size),
            fg_color=fg_color,
            text_color=text_color,
            wrap="word",
            activate_scrollbars=False,
        )
        content_label.insert("1.0", self.content)
        content_label.configure(state="disabled")  # Read-only

        # Calculate height based on content and font size
        num_lines = self.content.count("\n") + 1
        # Estimate line wrapping (adjust for font size)
        chars_per_line = int(60 * (14 / self.font_size))
        estimated_lines = max(num_lines, len(self.content) // chars_per_line + 1)
        line_height = int(20 * (self.font_size / 14))
        height = min(max(estimated_lines * line_height, 40), 400)  # Between 40 and 400px

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

    def update_font_size(self, font_size: int) -> None:
        """
        Update the font size of the message bubble.

        Args:
            font_size: New font size in pixels
        """
        # Update all text widgets
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkTextbox):
                # Update content textbox
                widget.configure(font=("", font_size))

                # Recalculate height based on new font size
                num_lines = self.content.count("\n") + 1
                chars_per_line = int(60 * (14 / font_size))  # Adjust for font size
                estimated_lines = max(num_lines, len(self.content) // chars_per_line + 1)
                line_height = int(20 * (font_size / 14))  # Scale line height
                height = min(max(estimated_lines * line_height, 40), 400)
                widget.configure(height=height)

            elif isinstance(widget, ctk.CTkLabel):
                # Update role label (keep it smaller than content)
                label_size = max(11, font_size - 3)
                widget.configure(font=("", label_size))
