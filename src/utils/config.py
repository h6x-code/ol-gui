"""
Configuration constants for Ol-GUI.
"""
from pathlib import Path

# Application info
APP_NAME = "ol-gui"
APP_DISPLAY_NAME = "Ol-GUI"
APP_VERSION = "0.0.1"

# Paths
CONFIG_DIR = Path.home() / ".config" / APP_NAME
DATA_DIR = Path.home() / ".local" / "share" / APP_NAME
SETTINGS_FILE = CONFIG_DIR / "settings.json"
DATABASE_FILE = DATA_DIR / "conversations.db"

# Default settings
DEFAULT_SETTINGS = {
    "theme": "dark",
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

# Color schemes
DARK_MODE_COLORS = {
    "background": "#1a1a1a",
    "surface": "#2d2d2d",
    "primary": "#4a9eff",
    "text": "#e0e0e0",
    "secondary_text": "#a0a0a0",
}

LIGHT_MODE_COLORS = {
    "background": "#ffffff",
    "surface": "#f5f5f5",
    "primary": "#2196f3",
    "text": "#1a1a1a",
    "secondary_text": "#666666",
}
