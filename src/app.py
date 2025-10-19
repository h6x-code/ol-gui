"""
Main application window for Ol-GUI.
"""
from typing import Optional
import customtkinter as ctk


class OllamaGUI(ctk.CTk):
    """Main application window for Ol-GUI."""

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()

        # Window configuration
        self.title("Ol-GUI")
        self.geometry("1200x800")

        # TODO: Initialize components
        # TODO: Load settings
        # TODO: Setup layout

    def run(self) -> None:
        """Start the application main loop."""
        self.mainloop()
