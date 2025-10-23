"""
Individual message bubble widget.
"""
import customtkinter as ctk
from typing import Literal, Optional, Dict
from utils.config import get_theme_colors


class MessageBubble(ctk.CTkFrame):
    """Widget for displaying a single message in the chat."""

    def __init__(
        self,
        parent,
        role: Literal["user", "assistant", "system"],
        content: str,
        font_size: int = 14,
        theme_colors: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Initialize a message bubble.

        Args:
            parent: Parent widget.
            role: Message role (user, assistant, or system).
            content: Message content text.
            font_size: Font size for the message text (default: 14).
            theme_colors: Optional theme color dictionary. Defaults to dark theme.
            **kwargs: Additional arguments for CTkFrame.
        """
        super().__init__(parent, **kwargs)

        self.role = role
        self.content = content
        self.font_size = font_size
        self.theme_colors = theme_colors or get_theme_colors("dark")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the message bubble UI."""
        # Configure frame with theme colors
        if self.role == "user":
            fg_color = self.theme_colors["user_bubble"]
            text_color = "#ffffff"  # White text for user messages
            anchor = "e"  # Right align
        elif self.role == "assistant":
            fg_color = self.theme_colors["assistant_bubble"]
            text_color = self.theme_colors["text"]
            anchor = "w"  # Left align
        else:  # system
            fg_color = self.theme_colors["system_bubble"]
            text_color = self.theme_colors["text_secondary"]
            anchor = "w"

        self.configure(fg_color=fg_color, corner_radius=10)

        # Role label (small text above message)
        label_color = text_color

        # Calculate role label font size (3 points smaller than content)
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
            activate_scrollbars=False,  # Disable scrollbars to force expansion
        )
        self.content_label.insert("1.0", self.content)
        self.content_label.configure(state="disabled")  # Read-only

        # Pack without expand, fill x only
        self.content_label.pack(pady=(0, 8), padx=12, fill="x", expand=False)

        # Calculate dynamic height based on actual content
        self._calculate_height()

    def _calculate_height(self) -> None:
        """Calculate and set the appropriate height for the message content."""
        # Check if widget still exists (may have been destroyed)
        try:
            if not self.winfo_exists():
                return
        except:
            return

        # Get actual width of the textbox (accounting for padding)
        try:
            self.update_idletasks()  # Ensure geometry is updated
            widget_width = self.content_label.winfo_width()
        except:
            # Widget was destroyed, exit gracefully
            return

        # If width is not available yet (initial setup), use estimate
        if widget_width <= 1:
            widget_width = 400  # Default estimate

        # Use the textbox's built-in measurement by counting lines with dlineinfo
        self.content_label.configure(state="normal")

        try:
            # Method: Use the Text widget's count method to get display lines
            # This accounts for actual wrapping that has occurred
            line_count = int(self.content_label.index('end-1c').split('.')[0])

            # More accurate approach: measure using bbox which gives actual pixel positions
            # Get bounding box of first and last character
            try:
                first_bbox = self.content_label.bbox("1.0")
                last_bbox = self.content_label.bbox("end-1c")

                if first_bbox and last_bbox:
                    # Calculate actual content height from bounding boxes
                    # bbox returns (x, y, width, height)
                    first_y = first_bbox[1]
                    last_y = last_bbox[1]
                    last_line_height = last_bbox[3]

                    # Total height is the difference plus the last line's height
                    measured_height = (last_y - first_y) + last_line_height

                    # Add very generous padding for top and bottom (80px to ensure no cutoff)
                    # Plus add an extra line's worth of space
                    final_height = measured_height + 80 + last_line_height
                else:
                    # bbox failed, fall back to line counting
                    raise ValueError("bbox returned None")

            except Exception:
                # Fallback to line-based calculation
                line_height = int(self.font_size * 1.6)  # Very generous line height
                final_height = (line_count * line_height) + 60

            # Ensure minimum height
            min_height = int(self.font_size * 1.4) * 2
            final_height = max(min_height, final_height)

        except Exception as e:
            # Ultimate fallback to estimation
            print(f"Height calculation error: {e}")
            avg_char_width = self.font_size * 0.5
            chars_per_line = max(int((widget_width - 30) / avg_char_width), 15)
            num_lines = self.content.count("\n") + 1
            estimated_wrapped_lines = (len(self.content) // chars_per_line) + 1
            total_lines = max(num_lines, estimated_wrapped_lines) + 4  # Extra buffer
            line_height = int(self.font_size * 1.6)  # Very generous
            final_height = max(line_height * 2, total_lines * line_height + 70)

        finally:
            self.content_label.configure(state="disabled")

        self.content_label.configure(height=final_height)

    def refresh_height(self) -> None:
        """
        Public method to refresh the message bubble height.

        This ensures the height is recalculated with current widget geometry,
        useful after window resizes or when loading conversations.
        """
        # Force geometry update before recalculating
        self.update_idletasks()
        # Wait for rendering to complete before measuring
        self.after(20, self._calculate_height)

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

    def update_theme_colors(self, theme_colors: Dict[str, str]) -> None:
        """
        Update the theme colors for this message bubble.

        Args:
            theme_colors: Dictionary of theme colors from config
        """
        self.theme_colors = theme_colors

        # Determine colors based on role
        if self.role == "user":
            fg_color = self.theme_colors["user_bubble"]
            text_color = "#ffffff"
        elif self.role == "assistant":
            fg_color = self.theme_colors["assistant_bubble"]
            text_color = self.theme_colors["text"]
        else:  # system
            fg_color = self.theme_colors["system_bubble"]
            text_color = self.theme_colors["text_secondary"]

        # Update frame color
        self.configure(fg_color=fg_color)

        # Update content label colors
        self.content_label.configure(fg_color=fg_color, text_color=text_color)

        # Update role label color
        self.role_label.configure(text_color=text_color)
