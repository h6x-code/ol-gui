"""
Settings management service.
"""
import json
from pathlib import Path
from typing import Any, Dict
from utils.config import SETTINGS_FILE, DEFAULT_SETTINGS, CONFIG_DIR


class SettingsManager:
    """Service for managing application settings."""

    def __init__(self, settings_file: Path = None) -> None:
        """
        Initialize the settings manager.

        Args:
            settings_file: Path to settings file. Defaults to SETTINGS_FILE.
        """
        self.settings_file = settings_file or SETTINGS_FILE
        self.settings: Dict[str, Any] = {}
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load settings from file, or use defaults if file doesn't exist."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in self.settings:
                        self.settings[key] = value
            except Exception as e:
                print(f"Error loading settings: {e}. Using defaults.")
                self.settings = DEFAULT_SETTINGS.copy()
        else:
            self.settings = DEFAULT_SETTINGS.copy()
            self.save()

    def save(self) -> None:
        """Save current settings to file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: The setting key.
            default: Default value if key doesn't exist.

        Returns:
            The setting value or default.
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value and save.

        Args:
            key: The setting key.
            value: The value to set.
        """
        self.settings[key] = value
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.

        Returns:
            Dictionary of all settings.
        """
        return self.settings.copy()
