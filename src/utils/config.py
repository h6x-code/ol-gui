"""
Configuration constants for Ol-GUI.
"""
from pathlib import Path

# Application info
APP_NAME = "ol-gui"
APP_DISPLAY_NAME = "Ol-GUI"
APP_VERSION = "0.1.0"

# Paths
CONFIG_DIR = Path.home() / ".config" / APP_NAME
DATA_DIR = Path.home() / ".local" / "share" / APP_NAME
SETTINGS_FILE = CONFIG_DIR / "settings.json"
DATABASE_FILE = DATA_DIR / "conversations.db"

# Default settings
DEFAULT_SETTINGS = {
    "theme": "dark",
    "custom_theme": None,  # For custom user-defined themes
    "font_size": 14,
    "last_model": "llama3.2",
    "window_width": 1200,
    "window_height": 800,
    "sidebar_width": 200,
    "auto_save": True,
    "stream_responses": True,
}

# UI Configuration
SIDEBAR_WIDTH = 200
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Built-in Theme Definitions
THEMES = {
    "dark": {
        "name": "Dark",
        "background": "#1a1a1a",
        "surface": "#2d2d2d",
        "primary": "#4a9eff",
        "primary_hover": "#3d8ee6",
        "text": "#e0e0e0",
        "text_secondary": "#a0a0a0",
        "border": "#444444",
        "user_bubble": "#4a9eff",
        "assistant_bubble": "#2d2d2d",
        "system_bubble": "#3d3d3d",
    },
    "light": {
        "name": "Light",
        "background": "#ffffff",
        "surface": "#f5f5f5",
        "primary": "#2196f3",
        "primary_hover": "#1976d2",
        "text": "#1a1a1a",
        "text_secondary": "#918383",
        "border": "#cccccc",
        "user_bubble": "#2196f3",
        "assistant_bubble": "#c0c0c0",
        "system_bubble": "#d0d0d0",
    },
    "monokai": {
        "name": "Monokai",
        "background": "#272822",
        "surface": "#3e3d32",
        "primary": "#f92672",
        "primary_hover": "#d91a5a",
        "text": "#f8f8f2",
        "text_secondary": "#d4cb9d",
        "border": "#49483e",
        "user_bubble": "#f92672",
        "assistant_bubble": "#3e3d32",
        "system_bubble": "#49483e",
    },
    "solarized_dark": {
        "name": "Solarized Dark",
        "background": "#002b36",
        "surface": "#073642",
        "primary": "#268bd2",
        "primary_hover": "#2075b8",
        "text": "#839496",
        "text_secondary": "#92bac6",
        "border": "#073642",
        "user_bubble": "#268bd2",
        "assistant_bubble": "#073642",
        "system_bubble": "#0d4759",
    },
    "nord": {
        "name": "Nord",
        "background": "#2e3440",
        "surface": "#3b4252",
        "primary": "#88c0d0",
        "primary_hover": "#6698a8",
        "text": "#eceff4",
        "text_secondary": "#d8dee9",
        "border": "#373f4e",
        "user_bubble": "#88c0d0",
        "assistant_bubble": "#3b4252",
        "system_bubble": "#434c5e",
    },
    "dracula": {
        "name": "Dracula",
        "background": "#282a36",
        "surface": "#44475a",
        "primary": "#bd93f9",
        "primary_hover": "#a87de0",
        "text": "#f8f8f2",
        "text_secondary": "#c2d1ff",
        "border": "#323442",
        "user_bubble": "#bd93f9",
        "assistant_bubble": "#44475a",
        "system_bubble": "#6272a4",
    },
    "okabe_ito": {
        "name": "Okabe-Ito",
        "background": "#000000",
        "surface": "#2d2d2d",
        "primary": "#56b4e9",
        "primary_hover": "#0072b2",
        "text": "#e0e0e0",
        "text_secondary": "#cc79a7",
        "border": "#f0e442",
        "user_bubble": "#d55e00",
        "assistant_bubble": "#2d2d2d",
        "system_bubble": "#3d3d3d",
    },
}

# Color schemes (for backwards compatibility)
DARK_MODE_COLORS = THEMES["dark"]
LIGHT_MODE_COLORS = THEMES["light"]


def get_theme_colors(theme_name: str):
    """
    Get color scheme for a theme.

    Args:
        theme_name: Name of the theme (dark, light, monokai, etc.)

    Returns:
        Dictionary of theme colors. Returns dark theme if theme not found.
    """
    return THEMES.get(theme_name, THEMES["dark"])
