"""
Sidebar component for model selection and conversation history.
"""
import customtkinter as ctk
from typing import Callable, List, Optional, Dict, Any


class Sidebar(ctk.CTkFrame):
    """Sidebar with model selection and conversation list."""

    def __init__(
        self,
        parent,
        on_model_change: Optional[Callable[[str], None]] = None,
        on_conversation_select: Optional[Callable[[int], None]] = None,
        on_new_conversation: Optional[Callable[[], None]] = None,
        on_delete_conversation: Optional[Callable[[int], None]] = None,
        **kwargs,
    ):
        """
        Initialize the sidebar.

        Args:
            parent: Parent widget.
            on_model_change: Callback when model is changed.
            on_conversation_select: Callback when conversation is selected.
            on_new_conversation: Callback when new conversation is requested.
            on_delete_conversation: Callback when conversation is deleted.
            **kwargs: Additional arguments for CTkFrame.
        """
        super().__init__(parent, **kwargs)

        self.on_model_change = on_model_change
        self.on_conversation_select = on_conversation_select
        self.on_new_conversation = on_new_conversation
        self.on_delete_conversation = on_delete_conversation

        self.current_conversation_id: Optional[int] = None
        self.conversation_buttons: Dict[int, ctk.CTkButton] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the sidebar UI."""
        self.configure(
            fg_color=("#f5f5f5", "#2d2d2d"),  # (light, dark)
            width=200,
            corner_radius=0,
        )

        # Header (blue stays same in both themes)
        self.header = ctk.CTkLabel(
            self,
            text="Ol-GUI",
            font=("", 20, "bold"),
            text_color=("#2196f3", "#4a9eff"),  # (light, dark)
        )
        self.header.pack(pady=(20, 10), padx=20)

        # New conversation button
        self.new_conv_btn = ctk.CTkButton(
            self,
            text="+ New Chat",
            command=self._handle_new_conversation,
            font=("", 14, "bold"),
            fg_color=("#2196f3", "#4a9eff"),  # (light, dark)
            hover_color=("#1976d2", "#3d8ee6"),
            height=40,
        )
        self.new_conv_btn.pack(pady=(0, 20), padx=20, fill="x")

        # Model selection section
        self.model_label = ctk.CTkLabel(
            self,
            text="Model",
            font=("", 12, "bold"),
            text_color=("#666666", "#a0a0a0"),  # (light, dark)
            anchor="w",
        )
        self.model_label.pack(pady=(10, 5), padx=20, fill="x")

        self.model_dropdown = ctk.CTkOptionMenu(
            self,
            values=["Loading..."],
            command=self._handle_model_change,
            font=("", 12),
            fg_color=("#888888", "#1a1a1a"),  # (light, dark)
            button_color=("#2196f3", "#4a9eff"),
            button_hover_color=("#1976d2", "#3d8ee6"),
        )
        self.model_dropdown.pack(pady=(0, 10), padx=20, fill="x")

        # Refresh models button
        self.refresh_btn = ctk.CTkButton(
            self,
            text="⟳ Refresh",
            command=self._handle_refresh_models,
            font=("", 11),
            text_color=("#000000", "#ffffff"),
            fg_color="transparent",
            hover_color=("#e0e0e0", "#3d3d3d"),  # (light, dark)
            height=30,
        )
        self.refresh_btn.pack(pady=(0, 20), padx=20, fill="x")

        # Separator
        self.separator = ctk.CTkFrame(self, height=2, fg_color=("#e0e0e0", "#1a1a1a"))
        self.separator.pack(fill="x", padx=20, pady=10)

        # Conversation history section
        self.history_label = ctk.CTkLabel(
            self,
            text="Conversations",
            font=("", 12, "bold"),
            text_color=("#666666", "#a0a0a0"),  # (light, dark)
            anchor="w",
        )
        self.history_label.pack(pady=(10, 5), padx=20, fill="x")

        # Scrollable frame for conversations
        self.conversations_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.conversations_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Settings button at bottom
        self.settings_btn = ctk.CTkButton(
            self,
            text="⚙ Settings",
            command=self._handle_settings,
            font=("", 12),
            fg_color="transparent",
            text_color=("#1a1a1a", "#e0e0e0"),  # (light, dark)
            hover_color=("#e0e0e0", "#3d3d3d"),  # (light, dark)
            height=35,
        )
        self.settings_btn.pack(side="bottom", pady=15, padx=20, fill="x")

    def _handle_model_change(self, model_name: str) -> None:
        """
        Handle model selection change.

        Args:
            model_name: Selected model name.
        """
        if self.on_model_change:
            self.on_model_change(model_name)

    def _handle_refresh_models(self) -> None:
        """Handle refresh models button click."""
        if hasattr(self, "on_refresh_models") and self.on_refresh_models:
            self.on_refresh_models()

    def _handle_new_conversation(self) -> None:
        """Handle new conversation button click."""
        if self.on_new_conversation:
            self.on_new_conversation()

    def _handle_settings(self) -> None:
        """Handle settings button click."""
        if hasattr(self, "on_settings") and self.on_settings:
            self.on_settings()

    def update_models(self, models: List[str], current_model: Optional[str] = None) -> None:
        """
        Update the model dropdown list.

        Args:
            models: List of available model names.
            current_model: Currently selected model (optional).
        """
        if not models:
            self.model_dropdown.configure(values=["No models available"])
            return

        self.model_dropdown.configure(values=models)

        if current_model and current_model in models:
            self.model_dropdown.set(current_model)
        elif models:
            self.model_dropdown.set(models[0])

    def add_conversation(self, conv_id: int, title: str, is_current: bool = False) -> None:
        """
        Add a conversation to the sidebar.

        Args:
            conv_id: Conversation ID.
            title: Conversation title.
            is_current: Whether this is the currently active conversation.
        """
        # Truncate long titles
        display_title = title[:30] + "..." if len(title) > 30 else title

        # Create button frame with delete option
        btn_frame = ctk.CTkFrame(self.conversations_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2, padx=5)

        # Conversation button
        conv_btn = ctk.CTkButton(
            btn_frame,
            text=display_title,
            command=lambda: self._handle_conversation_click(conv_id),
            font=("", 11),
            text_color="#e0e0e0" if is_current else ("#1a1a1a", "#e0e0e0"),  # (light, dark)
            fg_color="#4a9eff" if is_current else "transparent",
            hover_color="#3d8ee6" if is_current else "#3d3d3d",
            anchor="w",
            height=35,
        )
        conv_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Delete button (small)
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="×",
            command=lambda: self._handle_delete_click(conv_id),
            font=("", 16),
            text_color=("#1a1a1a", "#e0e0e0"),  # (light, dark)
            fg_color="transparent",
            hover_color=("#f27a6c", "#e74c3c"),
            width=30,
            height=35,
        )
        delete_btn.pack(side="right")

        self.conversation_buttons[conv_id] = conv_btn

        if is_current:
            self.current_conversation_id = conv_id

    def _handle_conversation_click(self, conv_id: int) -> None:
        """
        Handle conversation button click.

        Args:
            conv_id: Conversation ID.
        """
        # Update button colors
        for cid, btn in self.conversation_buttons.items():
            if cid == conv_id:
                btn.configure(fg_color="#4a9eff", hover_color="#3d8ee6")
            else:
                btn.configure(fg_color="transparent", hover_color="#3d3d3d")

        self.current_conversation_id = conv_id

        if self.on_conversation_select:
            self.on_conversation_select(conv_id)

    def _handle_delete_click(self, conv_id: int) -> None:
        """
        Handle conversation delete button click.

        Args:
            conv_id: Conversation ID to delete.
        """
        if self.on_delete_conversation:
            self.on_delete_conversation(conv_id)

    def remove_conversation(self, conv_id: int) -> None:
        """
        Remove a conversation from the sidebar.

        Args:
            conv_id: Conversation ID to remove.
        """
        if conv_id in self.conversation_buttons:
            # Find and destroy the parent frame
            btn = self.conversation_buttons[conv_id]
            btn_frame = btn.master
            btn_frame.destroy()

            del self.conversation_buttons[conv_id]

            if self.current_conversation_id == conv_id:
                self.current_conversation_id = None

    def clear_conversations(self) -> None:
        """Clear all conversations from the sidebar."""
        for widget in self.conversations_frame.winfo_children():
            widget.destroy()

        self.conversation_buttons.clear()
        self.current_conversation_id = None

    def set_refresh_models_callback(self, callback: Callable[[], None]) -> None:
        """
        Set the callback for refreshing models.

        Args:
            callback: Function to call when refresh is clicked.
        """
        self.on_refresh_models = callback

    def set_settings_callback(self, callback: Callable[[], None]) -> None:
        """
        Set the callback for opening settings.

        Args:
            callback: Function to call when settings is clicked.
        """
        self.on_settings = callback

    def update_theme(self, theme: str) -> None:
        """
        Update the sidebar theme colors.

        Args:
            theme: Theme name ("dark", "light", or "system")
        """
        if theme == "light":
            surface_color = "#f5f5f5"
            bg_color = "#ffffff"
            text_color = "#1a1a1a"
            secondary_text = "#666666"
            hover_color = "#e0e0e0"
        else:
            surface_color = "#2d2d2d"
            bg_color = "#1a1a1a"
            text_color = "#e0e0e0"
            secondary_text = "#a0a0a0"
            hover_color = "#3d3d3d"

        # Most widgets use color tuples and update automatically via set_appearance_mode()
        # No need to manually update sidebar, labels, buttons, etc.

        # Update all conversation buttons
        for conv_id, btn in self.conversation_buttons.items():
            is_current = (conv_id == self.current_conversation_id)
            if is_current:
                btn.configure(fg_color="#4a9eff", hover_color="#3d8ee6")
            else:
                btn.configure(fg_color="transparent", hover_color=hover_color)
