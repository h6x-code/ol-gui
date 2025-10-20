"""
Settings dialog component.
"""
import customtkinter as ctk
from typing import Callable, Optional


class SettingsDialog(ctk.CTkToplevel):
    """Dialog window for application settings."""

    def __init__(
        self,
        parent,
        settings_manager,
        on_save: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent window.
            settings_manager: SettingsManager instance.
            on_save: Callback function when settings are saved.
            **kwargs: Additional arguments for CTkToplevel.
        """
        super().__init__(parent, **kwargs)

        self.settings_manager = settings_manager
        self.on_save = on_save
        self.parent_app = parent  # Keep reference to parent app

        # Window configuration
        self.title("Settings")
        self.geometry("500x500")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)

        # Store original values for cancel
        self.original_settings = self.settings_manager.get_all().copy()

        self._setup_ui()

        # Center the dialog on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Now grab focus after window is visible
        self.after(10, self.grab_set)

    def _setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        # Configure dialog background
        self.configure(fg_color=("#ffffff", "#1a1a1a"))  # (light, dark)

        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#1a1a1a"))  # (light, dark)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Settings sections
        self._create_appearance_section(main_frame)
        self._create_general_section(main_frame)

        # Buttons at bottom
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            text_color=("#1a1a1a", "#e0e0e0"),
            command=self._on_cancel,
            fg_color="transparent",
            border_width=2,
            width=100,
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save,
            width=100,
        )
        save_btn.pack(side="right")

    def _create_appearance_section(self, parent) -> None:
        """Create appearance settings section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))  # (light, dark)
        section.pack(fill="x", pady=(0, 15))

        # Section title
        ctk.CTkLabel(
            section,
            text="Appearance",
            font=("", 16, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Theme selection
        theme_frame = ctk.CTkFrame(section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            width=120,
            anchor="w",
        ).pack(side="left")

        self.theme_var = ctk.StringVar(value=self.settings_manager.get("theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["dark", "light", "system"],
            command=self._on_theme_change,
        )
        theme_menu.pack(side="left", fill="x", expand=True)

        # Font size
        font_frame = ctk.CTkFrame(section, fg_color="transparent")
        font_frame.pack(fill="x", padx=5, pady=(5, 15))

        ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            width=120,
            anchor="w",
        ).pack(side="left")

        self.font_size_var = ctk.IntVar(value=self.settings_manager.get("font_size", 14))
        font_slider = ctk.CTkSlider(
            font_frame,
            from_=10,
            to=24,
            number_of_steps=14,
            variable=self.font_size_var,
        )
        font_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.font_size_label = ctk.CTkLabel(
            font_frame,
            text=f"{self.font_size_var.get()}px",
            width=40,
        )
        self.font_size_label.pack(side="left")

        # Update label when slider changes
        self.font_size_var.trace_add("write", self._update_font_size_label)

    def _create_general_section(self, parent) -> None:
        """Create general settings section."""
        section = ctk.CTkFrame(parent, fg_color=("#e0e0e0", "#2d2d2d"))  # (light, dark)
        section.pack(fill="x", pady=(0, 15))

        # Section title
        ctk.CTkLabel(
            section,
            text="General",
            font=("", 16, "bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Auto-save
        autosave_frame = ctk.CTkFrame(section, fg_color="transparent")
        autosave_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            autosave_frame,
            text="Auto-save conversations:",
            width=200,
            anchor="w",
        ).pack(side="left")

        self.autosave_var = ctk.BooleanVar(value=self.settings_manager.get("auto_save", True))
        autosave_switch = ctk.CTkSwitch(
            autosave_frame,
            text="",
            variable=self.autosave_var,
        )
        autosave_switch.pack(side="left")

        # Streaming
        stream_frame = ctk.CTkFrame(section, fg_color="transparent")
        stream_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            stream_frame,
            text="Stream responses:",
            width=200,
            anchor="w",
        ).pack(side="left")

        self.stream_var = ctk.BooleanVar(value=self.settings_manager.get("stream_responses", True))
        stream_switch = ctk.CTkSwitch(
            stream_frame,
            text="",
            variable=self.stream_var,
        )
        stream_switch.pack(side="left")

    def _update_font_size_label(self, *args) -> None:
        """Update the font size label when slider changes."""
        self.font_size_label.configure(text=f"{self.font_size_var.get()}px")

    def _on_theme_change(self, theme: str) -> None:
        """
        Handle theme change in dropdown - live preview.

        Args:
            theme: Selected theme name
        """
        # Apply theme immediately for preview
        ctk.set_appearance_mode(theme)
        self.update_theme(theme)

        # Also update parent app for live preview
        if hasattr(self.parent_app, '_apply_theme_colors'):
            self.parent_app._apply_theme_colors(theme)

    def _on_save(self) -> None:
        """Handle save button click."""
        # Save all settings
        self.settings_manager.set("theme", self.theme_var.get())
        self.settings_manager.set("font_size", self.font_size_var.get())
        self.settings_manager.set("auto_save", self.autosave_var.get())
        self.settings_manager.set("stream_responses", self.stream_var.get())

        # Call callback if provided
        if self.on_save:
            self.on_save()

        # Close dialog
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        # Restore original settings (don't save changes)
        self.destroy()

    def update_theme(self, theme: str) -> None:
        """
        Update the dialog theme colors.

        Args:
            theme: Theme name ("dark", "light", or "system")
        """
        if theme == "light":
            bg_color = "#ffffff"
            surface_color = "#e0e0e0"
            text_color = "#1a1a1a"
        else:
            bg_color = "#1a1a1a"
            surface_color = "#2d2d2d"
            text_color = "#e0e0e0"

        # Update dialog background
        self.configure(fg_color=bg_color)

        # Update all frames - need to traverse widget tree
        for widget in self.winfo_children():
            self._update_widget_theme(widget, bg_color, surface_color, text_color)

    def _update_widget_theme(self, widget, bg_color: str, surface_color: str, text_color: str) -> None:
        """
        Recursively update widget theme colors.

        Args:
            widget: Widget to update
            bg_color: Background color
            surface_color: Surface color
            text_color: Text color
        """
        # Update CTkFrame widgets
        if isinstance(widget, ctk.CTkFrame):
            current_fg = widget.cget("fg_color")
            # Only update if not transparent
            if current_fg != "transparent":
                # Main container uses bg, sections use surface
                if hasattr(widget, "winfo_children") and len(list(widget.winfo_children())) > 2:
                    widget.configure(fg_color=surface_color)
                else:
                    widget.configure(fg_color=bg_color)

        # Recursively update children
        if hasattr(widget, "winfo_children"):
            for child in widget.winfo_children():
                self._update_widget_theme(child, bg_color, surface_color, text_color)
