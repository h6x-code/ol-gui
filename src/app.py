"""
Main application window for Ol-GUI.
"""
import threading
from typing import Optional
import customtkinter as ctk

from components.sidebar import Sidebar
from components.chat_panel import ChatPanel
from components.input_panel import InputPanel
from services.ollama_service import OllamaService
from services.conversation_manager import ConversationManager
from services.settings_manager import SettingsManager
from services.export_service import ExportService
from services.search_service import SearchService
from models.message import Message
from models.conversation import Conversation
from utils.config import get_theme_colors


class OllamaGUI(ctk.CTk):
    """Main application window for Ol-GUI."""

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__(className="OL-GUI")

        # Initialize services
        self.settings = SettingsManager()
        self.ollama = OllamaService()
        self.conv_manager = ConversationManager()
        self.export_service = ExportService()
        self.search_service = SearchService(self.conv_manager)

        # Application state
        self.current_conversation: Optional[Conversation] = None
        self.current_model: str = self.settings.get("last_model", "llama3.2")
        self.is_generating: bool = False
        self._stop_generation: bool = False

        # Window configuration
        self._setup_window()

        # Setup UI
        self._setup_ui()

        # Apply saved font size
        font_size = self.settings.get("font_size", 14)
        self._apply_font_size(font_size)

        # Apply saved theme
        theme = self.settings.get("theme", "dark")
        self._apply_theme_colors(theme)

        # Load initial data
        self._load_initial_data()

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.title("OL-GUI")

        # Set app icon for dock/taskbar (Linux)
        try:
            from pathlib import Path
            from PIL import Image
            import tkinter as tk
            import io

            icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
            if icon_path.exists():
                img = Image.open(icon_path).convert('RGBA')
                with io.BytesIO() as output:
                    img.save(output, format='PPM')
                    ppm_data = output.getvalue()
                self._icon_photo = tk.PhotoImage(data=ppm_data)
                self.iconphoto(True, self._icon_photo)
        except Exception as e:
            print(f"Failed to load icon: {e}")

        # Load saved window size or use defaults
        width = self.settings.get("window_width", 1200)
        height = self.settings.get("window_height", 800)
        self.geometry(f"{width}x{height}")

        # Set minimum size
        self.minsize(800, 600)

        # Set theme
        theme = self.settings.get("theme", "dark")
        # Only set to dark/light for ctk appearance mode
        if theme in ["dark", "light"]:
            ctk.set_appearance_mode(theme)
        else:
            ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Save window size on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Initialize sidebar width
        self.sidebar_width = self.settings.get("sidebar_width", 350)

        # Get initial theme colors
        theme = self.settings.get("theme", "dark")
        theme_colors = get_theme_colors(theme)

        # Configure grid
        self.grid_columnconfigure(0, weight=0, minsize=self.sidebar_width)
        self.grid_columnconfigure(1, weight=0, minsize=4)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_model_change=self._on_model_change,
            on_conversation_select=self._on_conversation_select,
            on_new_conversation=self._on_new_conversation,
            on_delete_conversation=self._on_delete_conversation,
            theme_colors=theme_colors,
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.set_refresh_models_callback(self._refresh_models)
        self.sidebar.set_settings_callback(self._on_settings)
        self.sidebar.set_rename_conversation_callback(self._on_rename_conversation)
        self.sidebar.set_search_callback(self._on_search)

        # Resize separator
        self.separator = ctk.CTkFrame(self, width=4, fg_color=theme_colors["border"], cursor="sb_h_double_arrow")
        self.separator.grid(row=0, column=1, rowspan=2, sticky="ns")
        self.separator.bind("<Button-1>", self._start_resize)
        self.separator.bind("<B1-Motion>", self._do_resize)

        # Chat panel
        font_size = self.settings.get("font_size", 14)
        self.chat_panel = ChatPanel(self, font_size=font_size, theme_colors=theme_colors)
        self.chat_panel.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)

        # Input panel
        self.input_panel = InputPanel(
            self,
            on_send=self._on_send_message,
            theme_colors=theme_colors,
        )
        self.input_panel.grid(row=1, column=2, sticky="ew", padx=0, pady=0)
        self.input_panel.set_stop_callback(self._stop_generation_callback)

        # Bind window resize to constrain sidebar
        self.bind("<Configure>", self._on_window_resize)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for the application."""
        # Ctrl+N: New conversation
        self.bind("<Control-n>", lambda e: self._on_new_conversation())

        # Ctrl+S: Open settings
        self.bind("<Control-comma>", lambda e: self._on_settings())

        # Ctrl+F: Focus search (when implemented in sidebar)
        self.bind("<Control-f>", lambda e: self._focus_search())

        # Ctrl+E: Export current conversation
        self.bind("<Control-e>", lambda e: self._export_current_conversation())

        # Ctrl+W: Close current conversation (delete)
        # self.bind("<Control-w>", lambda e: self._close_current_conversation())

        # Escape: Stop generation if running
        self.bind("<Escape>", lambda e: self._stop_generation_callback() if self.is_generating else None)

    def _load_initial_data(self) -> None:
        """Load initial data (models, conversations)."""
        # Load models in background
        threading.Thread(target=self._refresh_models, daemon=True).start()

        # Load conversation history
        conversations = self._load_conversations()

        # Load most recent conversation, or create new one if none exist
        if conversations:
            most_recent = conversations[0]
            self._on_conversation_select(most_recent.id)
        else:
            self._on_new_conversation()

        # Recalculate message bubble heights after window is fully rendered
        self.after(100, self._recalculate_message_heights)

    def _refresh_models(self) -> None:
        """Refresh the list of available models."""
        try:
            models = self.ollama.list_models()
            model_names = [model.get("name", "unknown") for model in models]

            self.after(0, lambda: self.sidebar.update_models(
                model_names,
                self.current_model
            ))

            if self.current_model not in model_names and model_names:
                self.current_model = model_names[0]
                self.settings.set("last_model", self.current_model)

        except Exception as e:
            print(f"Failed to load models: {e}")
            self.after(0, lambda: self.sidebar.update_models(
                ["Error loading models"],
                None
            ))

    def _load_conversations(self):
        """Load conversation history into sidebar."""
        try:
            conversations = self.conv_manager.list_conversations()
            self.sidebar.clear_conversations()

            for conv in conversations:
                self.sidebar.add_conversation(
                    conv.id,
                    conv.title,
                    is_current=False
                )

            return conversations

        except Exception as e:
            print(f"Failed to load conversations: {e}")
            return []

    def _on_model_change(self, model_name: str) -> None:
        """Handle model selection change."""
        if self.current_model and self.current_model != model_name:
            self.ollama.cleanup(self.current_model)

        self.current_model = model_name
        self.settings.set("last_model", model_name)

        if self.current_conversation:
            self._on_new_conversation()

    def _on_new_conversation(self) -> None:
        """Create a new conversation."""
        try:
            title = f"Chat {self.conv_manager.list_conversations().__len__() + 1}"
            conv = self.conv_manager.create_conversation(title, self.current_model)

            self.current_conversation = conv
            self.chat_panel.clear_messages()

            self._load_conversations()
            self.sidebar._handle_conversation_click(conv.id)
            self.input_panel.focus_input()

        except Exception as e:
            print(f"Failed to create conversation: {e}")

    def _on_conversation_select(self, conv_id: int) -> None:
        """Handle conversation selection."""
        try:
            conv = self.conv_manager.get_conversation(conv_id)

            if conv:
                if self.current_model and self.current_model != conv.model:
                    self.ollama.cleanup(self.current_model)

                self.current_conversation = conv
                self.current_model = conv.model

                self.chat_panel.load_messages(conv.messages)
                self.sidebar.model_dropdown.set(conv.model)

                for cid, btn in self.sidebar.conversation_buttons.items():
                    if cid == conv_id:
                        btn.configure(
                            fg_color=self.sidebar.theme_colors["primary"],
                            text_color="#e0e0e0",
                            hover_color=self.sidebar.theme_colors["primary_hover"]
                        )
                    else:
                        btn.configure(
                            fg_color="transparent",
                            text_color=self.sidebar.theme_colors["text"],
                            hover_color=self.sidebar.theme_colors["border"]
                        )
                self.sidebar.current_conversation_id = conv_id

        except Exception as e:
            print(f"Failed to load conversation: {e}")

    def _on_rename_conversation(self, conv_id: int, new_title: str) -> None:
        """Handle conversation rename."""
        try:
            self.conv_manager.rename_conversation(conv_id, new_title)
            self.sidebar.update_conversation_title(conv_id, new_title)

            if self.current_conversation and self.current_conversation.id == conv_id:
                self.current_conversation.title = new_title

        except Exception as e:
            print(f"Failed to rename conversation: {e}")

    def _on_delete_conversation(self, conv_id: int) -> None:
        """Handle conversation deletion."""
        try:
            self.conv_manager.delete_conversation(conv_id)
            self.sidebar.remove_conversation(conv_id)

            if self.current_conversation and self.current_conversation.id == conv_id:
                self._on_new_conversation()

        except Exception as e:
            print(f"Failed to delete conversation: {e}")

    def _on_search(self, query: str) -> None:
        """Handle search query."""
        if not query.strip():
            return

        try:
            # Search across all conversations
            results = self.search_service.search(query, case_sensitive=False)

            # For now, just print results - could show in a dialog or highlight in chat
            print(f"Search results for '{query}': {len(results)} matches")
            for result in results[:5]:  # Show first 5
                snippet = self.search_service.highlight_matches(
                    result["content"], query, max_context=50
                )
                print(f"  - [{result['conversation_title']}] {snippet}")

        except Exception as e:
            print(f"Search failed: {e}")

    def _on_send_message(self, message_text: str) -> None:
        """Handle sending a message."""
        if not message_text.strip() or self.is_generating:
            return

        # Hidden commands
        command = message_text.strip().lower()

        if command == "/test-system":
            system_message = Message(role="system", content="This is a test system message.")
            self.chat_panel.add_message(system_message)
            return
        elif command in ["/bye", "/quit", "/exit"]:
            system_message = Message(role="system", content="Goodbye! Closing application...")
            self.chat_panel.add_message(system_message)
            self.after(1000, self._on_closing)
            return
        elif command == "/clear":
            self.chat_panel.clear_messages()
            system_message = Message(role="system", content="Conversation cleared.")
            self.chat_panel.add_message(system_message)
            return
        elif command == "/help":
            help_text = """Available commands:
/help - Show this help message
/test-system - Test system message colors
/clear - Clear current conversation
/bye, /quit, /exit - Close the application
Ctrl+N - New conversation
Ctrl+, - Settings
Ctrl+F - Search
Ctrl+E - Export conversation"""
            system_message = Message(role="system", content=help_text)
            self.chat_panel.add_message(system_message)
            return

        # Create user message
        user_message = Message(role="user", content=message_text)
        self.chat_panel.add_message(user_message)

        # Save to database
        if self.current_conversation and self.settings.get("auto_save", True):
            self.conv_manager.add_message(
                self.current_conversation.id,
                "user",
                message_text
            )
            conversations = self._load_conversations()
            if conversations and self.current_conversation:
                for conv in conversations:
                    if conv.id == self.current_conversation.id:
                        self.sidebar._handle_conversation_click(conv.id)
                        break

        # Generate response in background
        threading.Thread(
            target=self._generate_response,
            args=(message_text,),
            daemon=True
        ).start()

    def _generate_response(self, user_message: str) -> None:
        """Generate AI response in background thread."""
        self.is_generating = True
        self._stop_generation = False

        self.after(0, lambda: self.input_panel.set_sending_state(True))

        try:
            self.after(0, lambda: self.chat_panel.start_streaming_message("assistant"))

            generating_animation_running = [True]
            generating_dots = [0]

            def animate_generating():
                if not generating_animation_running[0]:
                    return
                dots = "." * (generating_dots[0] + 1)
                self.after(0, lambda: self.chat_panel.update_streaming_message(f"Generating response{dots}"))
                generating_dots[0] = (generating_dots[0] + 1) % 3
                if generating_animation_running[0]:
                    threading.Timer(0.5, animate_generating).start()

            animate_generating()

            # Get message history (includes system prompt if set)
            messages = []
            if self.current_conversation:
                conv = self.conv_manager.get_conversation(self.current_conversation.id)
                if conv:
                    messages = conv.get_message_history()
                    # Get model parameters from conversation
                    params = conv.model_parameters

            # Get response with model parameters
            full_response = ""
            use_streaming = self.settings.get("stream_responses", True)

            if use_streaming:
                response_stream = self.ollama.send_message(
                    self.current_model,
                    messages,
                    stream=True,
                    temperature=params.get("temperature"),
                    top_p=params.get("top_p"),
                    top_k=params.get("top_k"),
                    max_tokens=params.get("max_tokens"),
                )

                for chunk in response_stream:
                    if self._stop_generation:
                        break

                    if not full_response:
                        generating_animation_running[0] = False

                    full_response += chunk
                    self.after(0, lambda r=full_response: self.chat_panel.update_streaming_message(r))

                self.after(0, lambda: self.chat_panel.finish_streaming_message())
            else:
                response = self.ollama.send_message(
                    self.current_model,
                    messages,
                    stream=False,
                    temperature=params.get("temperature"),
                    top_p=params.get("top_p"),
                    top_k=params.get("top_k"),
                    max_tokens=params.get("max_tokens"),
                )

                generating_animation_running[0] = False

                if hasattr(response, 'message'):
                    full_response = response.message.content if response.message else ""
                elif isinstance(response, dict) and 'message' in response:
                    full_response = response['message'].get('content', '')

                assistant_message = Message(role="assistant", content=full_response)
                self.after(0, lambda: self.chat_panel.add_message(assistant_message))

            # Save assistant message
            if self.current_conversation and full_response and self.settings.get("auto_save", True):
                self.conv_manager.add_message(
                    self.current_conversation.id,
                    "assistant",
                    full_response
                )

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            error_message = Message(role="system", content=error_msg)
            self.after(0, lambda: self.chat_panel.add_message(error_message))

        finally:
            self.is_generating = False
            self.after(0, lambda: self.input_panel.set_sending_state(False))
            self.after(0, lambda: self.input_panel.focus_input())

    def _stop_generation_callback(self) -> None:
        """Stop the current generation."""
        self._stop_generation = True

    def _on_settings(self) -> None:
        """Open the settings dialog."""
        from components.settings_dialog import SettingsDialog

        dialog = SettingsDialog(
            self,
            self.settings,
            conversation=self.current_conversation,
            conversation_manager=self.conv_manager,
            export_service=self.export_service,
            on_save=self._on_settings_saved
        )

    def _on_settings_saved(self) -> None:
        """Handle settings being saved."""
        # Apply theme change
        theme = self.settings.get("theme", "dark")
        if theme in ["dark", "light"]:
            ctk.set_appearance_mode(theme)
        else:
            ctk.set_appearance_mode("dark")

        self._apply_theme_colors(theme)

        # Apply font size changes
        font_size = self.settings.get("font_size", 14)
        self._apply_font_size(font_size)

        # Reload current conversation to get updated parameters
        if self.current_conversation:
            conv = self.conv_manager.get_conversation(self.current_conversation.id)
            if conv:
                self.current_conversation = conv

    def _apply_theme_colors(self, theme: str) -> None:
        """Apply theme colors to all components."""
        # Get full theme colors dictionary
        theme_colors = get_theme_colors(theme)

        # Update separator
        self.separator.configure(fg_color=theme_colors["border"])

        # Update sidebar with theme colors
        if hasattr(self.sidebar, 'update_theme_colors'):
            self.sidebar.update_theme_colors(theme_colors)

        # Update chat panel with theme colors
        if hasattr(self.chat_panel, 'update_theme'):
            self.chat_panel.update_theme(theme_colors)

        # Update input panel with theme colors
        if hasattr(self.input_panel, 'update_theme'):
            self.input_panel.update_theme(theme_colors)

    def _focus_search(self) -> None:
        """Focus the search input in sidebar."""
        if hasattr(self.sidebar, 'focus_search'):
            self.sidebar.focus_search()

    def _export_current_conversation(self) -> None:
        """Export the current conversation."""
        if not self.current_conversation:
            return

        # Open settings dialog directly to export section
        self._on_settings()

    def _start_resize(self, event) -> None:
        """Handle start of sidebar resize."""
        self._resize_start_x = event.x_root

    def _do_resize(self, event) -> None:
        """Handle sidebar resize dragging."""
        mouse_x = event.x_root - self.winfo_rootx()
        min_width = 300
        max_width = self.winfo_width() // 2
        new_width = max(min_width, min(mouse_x, max_width))
        self.sidebar_width = new_width
        self.grid_columnconfigure(0, minsize=new_width)

    def _on_window_resize(self, event) -> None:
        """Handle window resize to constrain sidebar width."""
        if event.widget == self:
            max_width = self.winfo_width() // 2
            if self.sidebar_width > max_width:
                self.sidebar_width = max_width
                self.grid_columnconfigure(0, minsize=max_width)

    def _recalculate_message_heights(self) -> None:
        """Recalculate heights for all message bubbles."""
        if hasattr(self.chat_panel, 'message_widgets'):
            for bubble in self.chat_panel.message_widgets:
                if hasattr(bubble, '_calculate_height'):
                    bubble._calculate_height()

    def _apply_font_size(self, font_size: int) -> None:
        """Apply font size to all components."""
        if hasattr(self.sidebar, 'update_font_size'):
            self.sidebar.update_font_size(font_size)

        if hasattr(self.input_panel, 'input_text'):
            self.input_panel.input_text.configure(font=("", font_size))

        if hasattr(self.chat_panel, 'font_size'):
            self.chat_panel.font_size = font_size

        if hasattr(self.chat_panel, 'message_widgets'):
            for bubble in self.chat_panel.message_widgets:
                bubble.update_font_size(font_size)

    def _on_closing(self) -> None:
        """Handle window closing event."""
        self.settings.set("window_width", self.winfo_width())
        self.settings.set("window_height", self.winfo_height())
        self.settings.set("sidebar_width", self.sidebar_width)

        if self.current_model:
            self.ollama.cleanup(self.current_model)

        self.destroy()

    def run(self) -> None:
        """Start the application main loop."""
        self.mainloop()
