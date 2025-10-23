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
            fg_color = ("#e0e0e0", "#2d2d2d")  # Surface color for assistant (light, dark)
            text_color = ("#1a1a1a", "#f5f5f5")  # Text color (light, dark)
            anchor = "w"  # Left align
        else:  # system
            fg_color = ("#ffa33b", "#3d3d3d")  # Yellow/dark for system (light, dark)
            text_color = ("#1a1a1a", "#ffb96a")  # Text color (light, dark)
            anchor = "w"

        self.configure(fg_color=fg_color, corner_radius=10)

        # Role label (small text above message)
        label_color = text_color

        # Calculate role label font size (8 points larger than content)
        label_font_size = max(11, self.font_size - 3)

        self.role_label = ctk.CTkLabel(
            self,
            text=self.role.capitalize(),
            font=("", label_font_size),
            text_color=label_color,
            anchor=anchor,
        )
        self.role_label.pack(pady=(8, 2), padx=12, anchor=anchor, fill="x")

        # Message content
        self.content_label = ctk.CTkTextbox(
            self,
            font=("", self.font_size),
            fg_color=fg_color,
            text_color=text_color,
            wrap="word",
            activate_scrollbars=False,  # bubbles expand to fit content
        )
        self.content_label.insert("1.0", self.content)
        self.content_label.configure(state="disabled")  # Read-only

        # Pack without expand to allow proper height calculation
        self.content_label.pack(pady=(0, 8), padx=12, fill="x", expand=False)

        # Calculate dynamic height based on actual content
        self._calculate_height()

    def _calculate_height(self) -> None:
        """Calculate and set the appropriate height for the message content."""
        # Get actual width of the textbox (accounting for padding)
        self.update_idletasks()  # Ensure geometry is updated
        widget_width = self.content_label.winfo_width()

        # If width is not available yet (initial setup), use estimate
        if widget_width <= 1:
            widget_width = 400  # Default estimate

        # Calculate approximate characters per line based on font size
        # Use conservative estimate (0.45 instead of 0.5) to err on the side of taller bubbles
        # This accounts for variable-width fonts where some chars are wider
        avg_char_width = self.font_size * 0.45
        chars_per_line = int((widget_width - 30) / avg_char_width)  # More padding
        chars_per_line = max(chars_per_line, 15)  # Minimum reasonable width

        # Count actual newlines
        num_lines = self.content.count("\n") + 1

        # Estimate wrapped lines - add extra padding to prevent cutoff
        text_length = len(self.content)
        estimated_wrapped_lines = (text_length // chars_per_line) + 1

        # Add 1 extra line as buffer to prevent text cutoff
        estimated_wrapped_lines += 1

        # Total lines is the max of explicit newlines and wrapped lines
        total_lines = max(num_lines, estimated_wrapped_lines)

        # Calculate height with better font size scaling
        # Use 1.5 instead of 1.4 for more generous line height
        base_line_height = 1.5  # Line height multiplier (CSS-like)
        line_height = int(self.font_size * base_line_height)

        # Calculate total height with extra padding
        content_height = total_lines * line_height + 10  # Add 10px extra padding

        # Set reasonable min bound (no max to allow full expansion)
        min_height = line_height * 2  # At least 2 lines

        final_height = max(min_height, content_height)

        self.content_label.configure(height=final_height)

    def update_content(self, content: str) -> None:
        """
        Update the message content (for streaming responses).

        Args:
            content: New content text.
        """
        self.content = content

        # Update the textbox content
        self.content_label.configure(state="normal")
        self.content_label.delete("1.0", "end")
        self.content_label.insert("1.0", content)
        self.content_label.configure(state="disabled")

        # Recalculate height for new content
        self._calculate_height()

    def update_font_size(self, font_size: int) -> None:
        """
        Update the font size of the message bubble.

        Args:
            font_size: New font size in pixels
        """
        # Update stored font size
        self.font_size = font_size

        # Update content textbox font
        self.content_label.configure(font=("", font_size))

        # Update role label font (proportionally smaller)
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                label_size = max(11, font_size - 3)
                widget.configure(font=("", label_size))

        # Recalculate height with new font size
        self._calculate_height()
