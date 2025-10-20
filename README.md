# Ol-GUI

A sleek, minimalist GUI for [Ollama](https://ollama.ai) - interact with local LLMs through an elegant, customizable interface.

## Features

- **Clean Interface**: Distraction-free chat interface with message bubbles
- **Conversation Management**:
  - Create, rename, and delete conversations
  - Persistent conversation history stored locally
  - Auto-save conversations as you chat
- **Model Selection**: Switch between installed Ollama models on the fly
- **Customizable**:
  - Light and dark themes
  - Adjustable font size (10-24px)
  - Resizable sidebar (300px to half window width)
  - Settings persist between sessions
- **Smart Features**:
  - Streaming responses with "Thinking..." animation
  - Scrollable message bubbles for long responses
  - Window size and layout preferences saved automatically
  - Stop generation mid-response

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed and running locally
- `tkinter` (usually included with Python, or install via `sudo apt install python3-tk` on Linux)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/h6x-code/ol-gui.git
cd ol-gui
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running:
```bash
ollama serve
```

## Usage

Run the application:
```bash
python src/main.py
```

### Hidden Commands

Type these commands in the chat input:

- `/help` - Show available commands
- `/clear` - Clear current conversation
- `/test-system` - Test system message styling
- `/bye`, `/quit`, `/exit` - Close the application

### Tips

- **Resize the sidebar**: Drag the separator between the sidebar and chat panel
- **Rename conversations**: Click the ⋮ menu next to any conversation
- **Change models**: Select a different model from the dropdown - a new conversation will be created automatically
- **Adjust settings**: Click the ⚙ Settings button at the bottom of the sidebar

## Project Structure

```
ol-gui/
├── src/
│   ├── main.py                         # Application entry point
│   ├── app.py                          # Main application window
│   ├── components/                     # UI components
│   │   ├── sidebar.py                  # Model selection & conversation list
│   │   ├── chat_panel.py               # Message display area
│   │   ├── input_panel.py              # Message input
│   │   ├── message_bubble.py           # Individual message widget
│   │   └── settings_dialog.py          # Settings window
│   ├── services/                       # Backend services
│   │   ├── ollama_service.py           # Ollama API integration
│   │   ├── conversation_manager.py     # Database operations
│   │   └── settings_manager.py         # User preferences
│   ├── models/                         # Data models
│   │   ├── conversation.py
│   │   └── message.py
│   └── utils/                          # Utilities
│       ├── database.py                 # SQLite database
│       └── config.py                   # Configuration
├── requirements.txt
└── README.md
```

## Configuration

Settings are stored in `~/.config/ol-gui/`:
- `settings.json` - User preferences (theme, font size, window size, etc.)
- `conversations.db` - SQLite database with conversation history

## Development

Built with:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [Ollama Python SDK](https://github.com/ollama/ollama-python) - Ollama API client
- SQLite - Local conversation storage

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
