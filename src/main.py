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
    from app import OllamaGUI

    print("Ol-GUI starting...")

    try:
        app = OllamaGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
