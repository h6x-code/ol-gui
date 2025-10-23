"""
Settings dialog component.
"""
import customtkinter as ctk
from typing import Callable, Optional
from tkinter import filedialog
from pathlib import Path
from utils.config import THEMES


class SettingsDialog(ctk.CTkToplevel):
    """Dialog window for application settings."""

    def __init__(
        self,
        parent,
        settings_manager,
        conversation=None,
        conversation_manager=None,
        export_service=None,
        on_save: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent window.
            settings_manager: SettingsManager instance.
            conversation: Current conversation (for conversation-specific settings).
            conversation_manager: ConversationManager instance.
            export_service: ExportService instance for exporting conversations.
            on_save: Callback function when settings are saved.
            **kwargs: Additional arguments for CTkToplevel.
        """
        super().__init__(parent, **kwargs)

        self.settings_manager = settings_manager
        self.conversation = conversation
        self.conversation_manager = conversation_manager
        self.export_service = export_service
        self.on_save = on_save
        self.parent_app = parent

        # Window configuration
        self.title("Settings")
        self.geometry("1000x1400")

        # Make dialog modal
        self.transient(parent)

        # Store original values for cancel
        self.original_settings = self.settings_manager.get_all().copy()
        self.original_system_prompt = conversation.system_prompt if conversation else None
        self.original_model_params = conversation.model_parameters.copy() if conversation else {}

        # Get current font size for dialog display
        self.display_font_size = self.settings_manager.get("font_size", 14)

        self._setup_ui()

        # Center the dialog on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Grab focus after window is visible
        self.after(10, self.grab_set)

    def _setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        # Configure dialog background
        self.configure(fg_color=("#ffffff", "#1a1a1a"))

        # Main container with scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#ffffff", "#1a1a1a")
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Settings sections
        self._create_appearance_section(self.scrollable_frame)
        self._create_general_section(self.scrollable_frame)

        # Conversation-specific settings (if conversation provided)
        if self.conversation:
            self._create_conversation_section(self.scrollable_frame)

        # Export section (if conversation and export service provided)
        if self.conversation and self.export_service:
            self._create_export_section(self.scrollable_frame)

        # Buttons at bottom (fixed, not in scrollable frame)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            text_color=("#1a1a1a", "#e0e0e0"),
            command=self._on_cancel,
            fg_color="transparent",
            border_width=2,
            font=("", self.display_font_size),
            width=100,
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save,
            font=("", self.display_font_size),
            width=100,
        )
        save_btn.pack(side="right")

    def _create_appearance_section(self, parent) -> None:
        """Create appearance settings section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))
        section.pack(fill="x", pady=(0, 15))

        # Section title
        title_size = max(16, self.display_font_size + 2)
        ctk.CTkLabel(
            section,
            text="Appearance",
            font=("", title_size, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Theme selection
        theme_frame = ctk.CTkFrame(section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        # Get list of available themes - create mappings between keys and display names
        self.theme_key_to_name = {key: THEMES[key]["name"] for key in THEMES.keys()}
        self.theme_name_to_key = {THEMES[key]["name"]: key for key in THEMES.keys()}

        theme_display_names = list(self.theme_key_to_name.values())
        current_theme_key = self.settings_manager.get("theme", "dark")
        current_theme_name = self.theme_key_to_name.get(current_theme_key, "Dark")

        self.theme_var = ctk.StringVar(value=current_theme_name)
        dropdown_height = max(28, self.display_font_size + 14)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=theme_display_names,
            command=self._on_theme_change,
            font=("", self.display_font_size),
            dropdown_font=("", self.display_font_size),
            fg_color=("#2196f3", "#4a9eff"),
            button_color=("#2196f3", "#4a9eff"),
            button_hover_color=("#1976d2", "#3d8ee6"),
            anchor="w",
            height=dropdown_height,
        )
        theme_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Font size
        font_frame = ctk.CTkFrame(section, fg_color="transparent")
        font_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        self.font_size_var = ctk.IntVar(value=self.settings_manager.get("font_size", 14))
        font_slider = ctk.CTkSlider(
            font_frame,
            from_=10,
            to=36,
            number_of_steps=26,
            variable=self.font_size_var,
        )
        font_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.font_size_label = ctk.CTkLabel(
            font_frame,
            text=f"{self.font_size_var.get()}px",
            font=("", self.display_font_size),
            width=40,
        )
        self.font_size_label.pack(side="left")

        self.font_size_var.trace_add("write", self._update_font_size_label)

    def _create_general_section(self, parent) -> None:
        """Create general settings section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))
        section.pack(fill="x", pady=(0, 15))

        title_size = max(16, self.display_font_size + 2)
        ctk.CTkLabel(
            section,
            text="General",
            font=("", title_size, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Auto-save
        autosave_frame = ctk.CTkFrame(section, fg_color="transparent")
        autosave_frame.pack(fill="x", padx=15, pady=5)
        autosave_frame.grid_columnconfigure(0, weight=1)
        autosave_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            autosave_frame,
            text="Auto-save conversations:",
            font=("", self.display_font_size),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.autosave_var = ctk.BooleanVar(value=self.settings_manager.get("auto_save", True))
        switch_width = max(36, int(self.display_font_size * 2.2))
        switch_height = max(18, int(self.display_font_size * 1.1))
        ctk.CTkSwitch(
            autosave_frame,
            text="",
            variable=self.autosave_var,
            switch_width=switch_width,
            switch_height=switch_height,
        ).grid(row=0, column=1, sticky="e")

        # Streaming
        stream_frame = ctk.CTkFrame(section, fg_color="transparent")
        stream_frame.pack(fill="x", padx=15, pady=(5, 15))
        stream_frame.grid_columnconfigure(0, weight=1)
        stream_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            stream_frame,
            text="Stream responses:",
            font=("", self.display_font_size),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.stream_var = ctk.BooleanVar(value=self.settings_manager.get("stream_responses", True))
        ctk.CTkSwitch(
            stream_frame,
            text="",
            variable=self.stream_var,
            switch_width=switch_width,
            switch_height=switch_height,
        ).grid(row=0, column=1, sticky="e")

    def _create_conversation_section(self, parent) -> None:
        """Create conversation-specific settings section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))
        section.pack(fill="x", pady=(0, 15))

        title_size = max(16, self.display_font_size + 2)
        ctk.CTkLabel(
            section,
            text="Conversation Settings",
            font=("", title_size, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # System prompt
        ctk.CTkLabel(
            section,
            text="System Prompt:",
            font=("", self.display_font_size),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(5, 2))

        self.system_prompt_text = ctk.CTkTextbox(
            section,
            height=80,
            font=("", self.display_font_size),
        )
        self.system_prompt_text.pack(fill="x", padx=15, pady=(0, 10))

        if self.conversation.system_prompt:
            self.system_prompt_text.insert("1.0", self.conversation.system_prompt)

        # Model parameters
        ctk.CTkLabel(
            section,
            text="Model Parameters:",
            font=("", self.display_font_size, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(10, 5))

        # Temperature
        temp_frame = ctk.CTkFrame(section, fg_color="transparent")
        temp_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            temp_frame,
            text="Temperature:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        temp_value = self.conversation.model_parameters.get("temperature", 0.7)
        self.temperature_var = ctk.DoubleVar(value=temp_value)
        temp_slider = ctk.CTkSlider(
            temp_frame,
            from_=0.0,
            to=2.0,
            number_of_steps=40,
            variable=self.temperature_var,
        )
        temp_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.temperature_label = ctk.CTkLabel(
            temp_frame,
            text=f"{temp_value:.2f}",
            font=("", self.display_font_size),
            width=40,
        )
        self.temperature_label.pack(side="left")
        self.temperature_var.trace_add("write", lambda *args: self.temperature_label.configure(
            text=f"{self.temperature_var.get():.2f}"
        ))

        # Top P
        top_p_frame = ctk.CTkFrame(section, fg_color="transparent")
        top_p_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            top_p_frame,
            text="Top P:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        top_p_value = self.conversation.model_parameters.get("top_p", 0.9)
        self.top_p_var = ctk.DoubleVar(value=top_p_value)
        top_p_slider = ctk.CTkSlider(
            top_p_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            variable=self.top_p_var,
        )
        top_p_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.top_p_label = ctk.CTkLabel(
            top_p_frame,
            text=f"{top_p_value:.2f}",
            font=("", self.display_font_size),
            width=40,
        )
        self.top_p_label.pack(side="left")
        self.top_p_var.trace_add("write", lambda *args: self.top_p_label.configure(
            text=f"{self.top_p_var.get():.2f}"
        ))

        # Top K
        top_k_frame = ctk.CTkFrame(section, fg_color="transparent")
        top_k_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            top_k_frame,
            text="Top K:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        top_k_value = self.conversation.model_parameters.get("top_k", 40)
        self.top_k_var = ctk.IntVar(value=top_k_value)
        top_k_slider = ctk.CTkSlider(
            top_k_frame,
            from_=1,
            to=100,
            number_of_steps=99,
            variable=self.top_k_var,
        )
        top_k_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.top_k_label = ctk.CTkLabel(
            top_k_frame,
            text=f"{top_k_value}",
            font=("", self.display_font_size),
            width=40,
        )
        self.top_k_label.pack(side="left")
        self.top_k_var.trace_add("write", lambda *args: self.top_k_label.configure(
            text=f"{self.top_k_var.get()}"
        ))

        # Max Tokens
        max_tokens_frame = ctk.CTkFrame(section, fg_color="transparent")
        max_tokens_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            max_tokens_frame,
            text="Max Tokens:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        max_tokens_value = self.conversation.model_parameters.get("max_tokens", 2048)
        self.max_tokens_var = ctk.IntVar(value=max_tokens_value)
        max_tokens_slider = ctk.CTkSlider(
            max_tokens_frame,
            from_=128,
            to=8192,
            number_of_steps=63,
            variable=self.max_tokens_var,
        )
        max_tokens_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.max_tokens_label = ctk.CTkLabel(
            max_tokens_frame,
            text=f"{max_tokens_value}",
            font=("", self.display_font_size),
            width=50,
        )
        self.max_tokens_label.pack(side="left")
        self.max_tokens_var.trace_add("write", lambda *args: self.max_tokens_label.configure(
            text=f"{self.max_tokens_var.get()}"
        ))

    def _create_export_section(self, parent) -> None:
        """Create export section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))
        section.pack(fill="x", pady=(0, 15))

        title_size = max(16, self.display_font_size + 2)
        ctk.CTkLabel(
            section,
            text="Export Conversation",
            font=("", title_size, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Format selection
        format_frame = ctk.CTkFrame(section, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            format_frame,
            text="Format:",
            font=("", self.display_font_size),
            width=120,
            anchor="w",
        ).pack(side="left")

        self.export_format_var = ctk.StringVar(value="markdown")
        dropdown_height = max(28, self.display_font_size + 14)
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            variable=self.export_format_var,
            values=["markdown", "json", "text"],
            font=("", self.display_font_size),
            dropdown_font=("", self.display_font_size),
            anchor="w",
            height=dropdown_height,
        )
        format_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Export button
        export_btn = ctk.CTkButton(
            section,
            text="Export to File...",
            command=self._on_export,
            font=("", self.display_font_size),
            height=35,
        )
        export_btn.pack(fill="x", padx=15, pady=(5, 15))

    def _update_font_size_label(self, *args) -> None:
        """Update the font size label when slider changes."""
        self.font_size_label.configure(text=f"{self.font_size_var.get()}px")

    def _on_theme_change(self, theme_display_name: str) -> None:
        """
        Handle theme change in dropdown - live preview.

        Args:
            theme_display_name: Selected theme display name
        """
        # Convert display name to theme key
        theme_key = self.theme_name_to_key.get(theme_display_name, "dark")

        # Apply theme immediately for preview
        ctk.set_appearance_mode(theme_key if theme_key in ["dark", "light"] else "dark")
        self.update_theme(theme_key)

        # Also update parent app for live preview
        if hasattr(self.parent_app, '_apply_theme_colors'):
            self.parent_app._apply_theme_colors(theme_key)

    def _on_export(self) -> None:
        """Handle export button click."""
        if not self.export_service or not self.conversation:
            return

        format_type = self.export_format_var.get()

        # Generate default filename
        default_filename = self.export_service.get_default_filename(
            self.conversation,
            format_type
        )

        # Show save file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Conversation",
            defaultextension=f".{format_type}",
            initialfile=default_filename,
            filetypes=[
                ("Markdown files", "*.md") if format_type == "markdown" else
                ("JSON files", "*.json") if format_type == "json" else
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                self.export_service.export_conversation(
                    self.conversation,
                    format_type,
                    Path(file_path)
                )
                # Show success message (could use a toast notification)
                print(f"Exported to {file_path}")
            except Exception as e:
                print(f"Export failed: {e}")

    def _on_save(self) -> None:
        """Handle save button click."""
        # Save global settings (convert display name back to theme key)
        theme_display_name = self.theme_var.get()
        theme_key = self.theme_name_to_key.get(theme_display_name, "dark")
        self.settings_manager.set("theme", theme_key)
        self.settings_manager.set("font_size", self.font_size_var.get())
        self.settings_manager.set("auto_save", self.autosave_var.get())
        self.settings_manager.set("stream_responses", self.stream_var.get())

        # Save conversation-specific settings
        if self.conversation and self.conversation_manager:
            # Update system prompt
            system_prompt = self.system_prompt_text.get("1.0", "end-1c").strip()
            self.conversation_manager.update_system_prompt(
                self.conversation.id,
                system_prompt if system_prompt else None
            )

            # Update model parameters
            model_params = {
                "temperature": self.temperature_var.get(),
                "top_p": self.top_p_var.get(),
                "top_k": self.top_k_var.get(),
                "max_tokens": self.max_tokens_var.get(),
            }
            self.conversation_manager.update_model_parameters(
                self.conversation.id,
                model_params
            )

            # Update conversation object
            self.conversation.system_prompt = system_prompt if system_prompt else None
            self.conversation.model_parameters = model_params

        # Call callback if provided
        if self.on_save:
            self.on_save()

        # Close dialog
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        # Restore original theme if changed
        original_theme_key = self.original_settings.get("theme", "dark")
        current_theme_display_name = self.theme_var.get()
        current_theme_key = self.theme_name_to_key.get(current_theme_display_name, "dark")

        if original_theme_key != current_theme_key:
            ctk.set_appearance_mode(original_theme_key if original_theme_key in ["dark", "light"] else "dark")
            if hasattr(self.parent_app, '_apply_theme_colors'):
                self.parent_app._apply_theme_colors(original_theme_key)

        self.destroy()

    def update_theme(self, theme: str) -> None:
        """
        Update the dialog theme colors.

        Args:
            theme: Theme name
        """
        from utils.config import get_theme_colors

        colors = get_theme_colors(theme)

        # Update dialog background
        self.configure(fg_color=colors["background"])

        # Update scrollable frame
        if hasattr(self, 'scrollable_frame'):
            self.scrollable_frame.configure(fg_color=colors["background"])

        # Update all frames
        for widget in self.winfo_children():
            self._update_widget_theme(widget, colors)

    def _update_widget_theme(self, widget, colors) -> None:
        """
        Recursively update widget theme colors.

        Args:
            widget: Widget to update
            colors: Dictionary of theme colors
        """
        # Update CTkFrame widgets
        if isinstance(widget, ctk.CTkFrame):
            current_fg = widget.cget("fg_color")
            if current_fg != "transparent":
                # Sections use surface color, main container uses background
                if hasattr(widget, "winfo_children") and len(list(widget.winfo_children())) > 2:
                    widget.configure(fg_color=colors["surface"])
                else:
                    widget.configure(fg_color=colors["background"])

        # Recursively update children
        if hasattr(widget, "winfo_children"):
            for child in widget.winfo_children():
                self._update_widget_theme(child, colors)
