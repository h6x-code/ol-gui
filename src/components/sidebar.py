"""
Sidebar component for model selection and conversation history.
"""
import customtkinter as ctk
from typing import Callable, List, Optional, Dict


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
        self.current_font_size: int = 14  # Default font size, will be updated

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the sidebar UI."""
        self.configure(
            fg_color=("#e0e0e0", "#2d2d2d"),  # (light, dark)
            corner_radius=0,
        )

        # Header (blue stays same in both themes)
        self.header = ctk.CTkLabel(
            self,
            text="Ol-GUI",
            font=("", 24, "bold"),
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

        # Bind mouse wheel scrolling for conversations frame
        self._bind_conversations_mouse_wheel()

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

        # Calculate font size for conversation button (scaled from current font size)
        conv_font_size = max(10, self.current_font_size - 3)

        # Conversation button
        conv_btn = ctk.CTkButton(
            btn_frame,
            text=display_title,
            command=lambda: self._handle_conversation_click(conv_id),
            font=("", conv_font_size),
            text_color=("#1a1a1a", "#e0e0e0"),  # (light, dark)
            fg_color="#4a9eff" if is_current else "transparent",
            hover_color="#3d8ee6" if is_current else "#3d3d3d",
            anchor="w",
            height=35,
        )
        conv_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Options button (three dots)
        options_btn = ctk.CTkButton(
            btn_frame,
            text="⋮",
            command=lambda: self._show_conversation_options(conv_id, options_btn),
            font=("", 18),
            text_color=("#1a1a1a", "#e0e0e0"),  # (light, dark)
            fg_color="transparent",
            hover_color=("#e0e0e0", "#3d3d3d"),
            width=30,
            height=35,
        )
        options_btn.pack(side="right")

        self.conversation_buttons[conv_id] = conv_btn

        if is_current:
            # Deselect all other conversations
            for cid, btn in self.conversation_buttons.items():
                if cid != conv_id:
                    btn.configure(fg_color="transparent", hover_color="#3d3d3d")

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

    def _show_conversation_options(self, conv_id: int, button_widget) -> None:
        """
        Show options menu for a conversation.

        Args:
            conv_id: Conversation ID.
            button_widget: The button widget that triggered the menu.
        """
        # Create a menu
        menu = ctk.CTkToplevel(self)
        menu.withdraw()  # Hide initially
        menu.overrideredirect(True)  # Remove window decorations

        # Configure menu appearance
        menu.configure(fg_color=("#ffffff", "#2d2d2d"))

        # Create menu frame
        menu_frame = ctk.CTkFrame(
            menu,
            fg_color=("#ffffff", "#2d2d2d"),
            border_width=1,
            border_color=("#cccccc", "#555555"),
        )
        menu_frame.pack(fill="both", expand=True)

        # Rename option
        rename_btn = ctk.CTkButton(
            menu_frame,
            text="Rename",
            command=lambda: self._handle_rename_click(conv_id, menu),
            fg_color="transparent",
            text_color=("#1a1a1a", "#e0e0e0"),
            hover_color=("#e0e0e0", "#3d3d3d"),
            anchor="w",
            height=30,
        )
        rename_btn.pack(fill="x", padx=5, pady=(5, 2))

        # Delete option
        delete_btn = ctk.CTkButton(
            menu_frame,
            text="Delete",
            command=lambda: self._handle_delete_click(conv_id, menu),
            fg_color="transparent",
            text_color=("#1a1a1a", "#e0e0e0"),
            hover_color=("#ee9a90", "#c0392b"),
            anchor="w",
            height=30,
        )
        delete_btn.pack(fill="x", padx=5, pady=(2, 5))

        # Position menu near the button
        button_x = button_widget.winfo_rootx()
        button_y = button_widget.winfo_rooty()
        menu.geometry(f"120x70+{button_x - 90}+{button_y + 35}")

        # Show menu
        menu.deiconify()
        menu.lift()

        # Close menu when clicking outside
        def close_menu(event=None):
            if menu.winfo_exists():
                menu.destroy()

        # Bind to click events outside the menu
        def on_click_outside(event):
            # Check if click is outside the menu
            x, y = event.x_root, event.y_root
            menu_x = menu.winfo_rootx()
            menu_y = menu.winfo_rooty()
            menu_width = menu.winfo_width()
            menu_height = menu.winfo_height()

            if not (menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height):
                close_menu()

        # Bind escape key
        menu.bind("<Escape>", close_menu)

        # Bind click event to root window after a short delay
        menu.after(100, lambda: menu.master.bind("<Button-1>", on_click_outside, add="+"))

        # Clean up binding when menu is destroyed
        def on_destroy(event=None):
            try:
                menu.master.unbind("<Button-1>")
            except:
                pass

        menu.bind("<Destroy>", on_destroy)

    def _handle_rename_click(self, conv_id: int, menu) -> None:
        """
        Handle conversation rename option click.

        Args:
            conv_id: Conversation ID to rename.
            menu: The options menu to close.
        """
        menu.destroy()

        # Create rename dialog
        dialog = ctk.CTkInputDialog(
            text="Enter new name:",
            title="Rename Conversation"
        )
        new_title = dialog.get_input()

        if new_title and new_title.strip():
            # Call rename callback if it exists
            if hasattr(self, "on_rename_conversation") and self.on_rename_conversation:
                self.on_rename_conversation(conv_id, new_title.strip())

    def _handle_delete_click(self, conv_id: int, menu=None) -> None:
        """
        Handle conversation delete option click.

        Args:
            conv_id: Conversation ID to delete.
            menu: The options menu to close (optional).
        """
        if menu:
            menu.destroy()

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

    def set_rename_conversation_callback(self, callback: Callable[[int, str], None]) -> None:
        """
        Set the callback for renaming a conversation.

        Args:
            callback: Function to call when a conversation is renamed.
                     Takes (conv_id, new_title) as arguments.
        """
        self.on_rename_conversation = callback

    def update_conversation_title(self, conv_id: int, new_title: str) -> None:
        """
        Update the displayed title of a conversation.

        Args:
            conv_id: Conversation ID.
            new_title: New title to display.
        """
        if conv_id in self.conversation_buttons:
            # Truncate long titles
            display_title = new_title[:30] + "..." if len(new_title) > 30 else new_title
            self.conversation_buttons[conv_id].configure(text=display_title)

    def update_theme(self, theme: str) -> None:
        """
        Update the sidebar theme colors.

        Args:
            theme: Theme name ("dark", "light", or "system")
        """
        # Determine hover color based on theme
        hover_color = "#e0e0e0" if theme == "light" else "#3d3d3d"

        # Most widgets use color tuples and update automatically via set_appearance_mode()
        # No need to manually update sidebar, labels, buttons, etc.

        # Update all conversation buttons
        for conv_id, btn in self.conversation_buttons.items():
            is_current = (conv_id == self.current_conversation_id)
            if is_current:
                btn.configure(fg_color="#4a9eff", hover_color="#3d8ee6")
            else:
                btn.configure(fg_color="transparent", hover_color=hover_color)

    def update_font_size(self, font_size: int) -> None:
        """
        Update the sidebar font sizes.

        Args:
            font_size: Base font size in pixels
        """
        # Store current font size for new conversation buttons
        self.current_font_size = font_size

        # Scale sidebar fonts relative to base font size
        # Sidebar uses smaller fonts than main content
        header_size = max(24, font_size + 24)  # Header slightly larger
        button_size = max(12, font_size - 1)  # Buttons slightly smaller
        label_size = max(11, font_size - 2)   # Labels smaller

        # Update header
        self.header.configure(font=("", header_size, "bold"))

        # Update new chat button
        self.new_conv_btn.configure(font=("", button_size, "bold"))

        # Update labels
        self.model_label.configure(font=("", label_size, "bold"))
        self.history_label.configure(font=("", label_size, "bold"))

        # Update model dropdown
        self.model_dropdown.configure(font=("", button_size))

        # Update buttons
        self.refresh_btn.configure(font=("", max(10, font_size - 3)))
        self.settings_btn.configure(font=("", button_size))

        # Update conversation buttons
        for btn in self.conversation_buttons.values():
            btn.configure(font=("", max(10, font_size - 3)))

    def _bind_conversations_mouse_wheel(self) -> None:
        """Bind mouse wheel events for scrolling when mouse enters conversations frame."""
        # Bind mouse wheel only when mouse is over this widget
        self.conversations_frame.bind("<Enter>", self._on_conversations_mouse_enter)
        self.conversations_frame.bind("<Leave>", self._on_conversations_mouse_leave)

    def _on_conversations_mouse_enter(self, event) -> None:
        """Enable mouse wheel scrolling when mouse enters the conversations frame."""
        if hasattr(self.conversations_frame, '_parent_canvas'):
            # Linux scroll (Button-4/5)
            self.conversations_frame._parent_canvas.bind_all("<Button-4>", self._on_conversations_mouse_wheel)
            self.conversations_frame._parent_canvas.bind_all("<Button-5>", self._on_conversations_mouse_wheel)

    def _on_conversations_mouse_leave(self, event) -> None:
        """Disable mouse wheel scrolling when mouse leaves the conversations frame."""
        if hasattr(self.conversations_frame, '_parent_canvas'):
            # Unbind mouse wheel events
            self.conversations_frame._parent_canvas.unbind_all("<Button-4>")
            self.conversations_frame._parent_canvas.unbind_all("<Button-5>")

    def _on_conversations_mouse_wheel(self, event) -> None:
        """
        Handle mouse wheel scrolling for conversations frame.

        Args:
            event: Mouse wheel event.
        """
        if hasattr(self.conversations_frame, '_parent_canvas'):
            # Linux uses Button-4 (scroll up) and Button-5 (scroll down)
            if event.num == 4:
                self.conversations_frame._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.conversations_frame._parent_canvas.yview_scroll(1, "units")
            # Windows/Mac use event.delta
            elif hasattr(event, 'delta'):
                self.conversations_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
