#!/usr/bin/env python3
"""
Ol-GUI - Main entry point for the application.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    """Main entry point for Ol-GUI."""
    # TODO: Initialize and run the application
    print("Ol-GUI starting...")
    # from app import OllamaGUI
    # app = OllamaGUI()
    # app.run()


if __name__ == "__main__":
    main()
