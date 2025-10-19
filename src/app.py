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
from models.message import Message
from models.conversation import Conversation


class OllamaGUI(ctk.CTk):
    """Main application window for Ol-GUI."""

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()

        # Initialize services
        self.settings = SettingsManager()
        self.ollama = OllamaService()
        self.conv_manager = ConversationManager()

        # Application state
        self.current_conversation: Optional[Conversation] = None
        self.current_model: str = self.settings.get("last_model", "llama3.2")
        self.is_generating: bool = False
        self._stop_generation: bool = False

        # Window configuration
        self._setup_window()

        # Setup UI
        self._setup_ui()

        # Load initial data
        self._load_initial_data()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.title("Ol-GUI")

        # Load saved window size or use defaults
        width = self.settings.get("window_width", 1200)
        height = self.settings.get("window_height", 800)
        self.geometry(f"{width}x{height}")

        # Set minimum size
        self.minsize(800, 600)

        # Set theme
        theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # Save window size on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_model_change=self._on_model_change,
            on_conversation_select=self._on_conversation_select,
            on_new_conversation=self._on_new_conversation,
            on_delete_conversation=self._on_delete_conversation,
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.set_refresh_models_callback(self._refresh_models)

        # Chat panel
        self.chat_panel = ChatPanel(self)
        self.chat_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Input panel
        self.input_panel = InputPanel(
            self,
            on_send=self._on_send_message,
        )
        self.input_panel.grid(row=1, column=1, sticky="ew", padx=0, pady=0)
        self.input_panel.set_stop_callback(self._stop_generation_callback)

    def _load_initial_data(self) -> None:
        """Load initial data (models, conversations)."""
        # Load models in background
        threading.Thread(target=self._refresh_models, daemon=True).start()

        # Load conversation history
        self._load_conversations()

        # Create a new conversation by default
        self._on_new_conversation()

    def _refresh_models(self) -> None:
        """Refresh the list of available models."""
        try:
            models = self.ollama.list_models()
            model_names = [model.get("name", "unknown") for model in models]

            # Update UI in main thread
            self.after(0, lambda: self.sidebar.update_models(
                model_names,
                self.current_model
            ))

            # Check if current model exists
            if self.current_model not in model_names and model_names:
                self.current_model = model_names[0]
                self.settings.set("last_model", self.current_model)

        except Exception as e:
            print(f"Failed to load models: {e}")
            self.after(0, lambda: self.sidebar.update_models(
                ["Error loading models"],
                None
            ))

    def _load_conversations(self) -> None:
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

        except Exception as e:
            print(f"Failed to load conversations: {e}")

    def _on_model_change(self, model_name: str) -> None:
        """
        Handle model selection change.

        Args:
            model_name: Selected model name.
        """
        self.current_model = model_name
        self.settings.set("last_model", model_name)

        # Update current conversation's model if exists
        if self.current_conversation:
            # Create new conversation with new model
            self._on_new_conversation()

    def _on_new_conversation(self) -> None:
        """Create a new conversation."""
        try:
            # Create conversation in database
            title = f"Chat {self.conv_manager.list_conversations().__len__() + 1}"
            conv = self.conv_manager.create_conversation(title, self.current_model)

            # Update UI
            self.current_conversation = conv
            self.chat_panel.clear_messages()

            # Add to sidebar
            self.sidebar.add_conversation(conv.id, conv.title, is_current=True)

            # Focus input
            self.input_panel.focus_input()

        except Exception as e:
            print(f"Failed to create conversation: {e}")

    def _on_conversation_select(self, conv_id: int) -> None:
        """
        Handle conversation selection.

        Args:
            conv_id: Selected conversation ID.
        """
        try:
            # Load conversation from database
            conv = self.conv_manager.get_conversation(conv_id)

            if conv:
                self.current_conversation = conv
                self.current_model = conv.model

                # Update UI
                self.chat_panel.load_messages(conv.messages)
                self.sidebar.model_dropdown.set(conv.model)

        except Exception as e:
            print(f"Failed to load conversation: {e}")

    def _on_delete_conversation(self, conv_id: int) -> None:
        """
        Handle conversation deletion.

        Args:
            conv_id: Conversation ID to delete.
        """
        try:
            # Delete from database
            self.conv_manager.delete_conversation(conv_id)

            # Update UI
            self.sidebar.remove_conversation(conv_id)

            # If current conversation was deleted, create new one
            if self.current_conversation and self.current_conversation.id == conv_id:
                self._on_new_conversation()

        except Exception as e:
            print(f"Failed to delete conversation: {e}")

    def _on_send_message(self, message_text: str) -> None:
        """
        Handle sending a message.

        Args:
            message_text: The message text to send.
        """
        if not message_text.strip() or self.is_generating:
            return

        # Create user message
        user_message = Message(role="user", content=message_text)

        # Add to UI
        self.chat_panel.add_message(user_message)

        # Save to database
        if self.current_conversation:
            self.conv_manager.add_message(
                self.current_conversation.id,
                "user",
                message_text
            )

        # Generate response in background
        threading.Thread(
            target=self._generate_response,
            args=(message_text,),
            daemon=True
        ).start()

    def _generate_response(self, user_message: str) -> None:
        """
        Generate AI response in background thread.

        Args:
            user_message: The user's message.
        """
        self.is_generating = True
        self._stop_generation = False

        # Update UI state
        self.after(0, lambda: self.input_panel.set_sending_state(True))

        try:
            # Start streaming message
            self.after(0, lambda: self.chat_panel.start_streaming_message("assistant"))

            # Get message history
            messages = []
            if self.current_conversation:
                conv = self.conv_manager.get_conversation(self.current_conversation.id)
                if conv:
                    messages = conv.get_message_history()

            # Stream response
            full_response = ""
            response_stream = self.ollama.send_message(
                self.current_model,
                messages,
                stream=True
            )

            for chunk in response_stream:
                if self._stop_generation:
                    break

                full_response += chunk
                # Update UI in main thread
                self.after(0, lambda r=full_response: self.chat_panel.update_streaming_message(r))

            # Finish streaming
            self.after(0, lambda: self.chat_panel.finish_streaming_message())

            # Save assistant message to database
            if self.current_conversation and full_response:
                self.conv_manager.add_message(
                    self.current_conversation.id,
                    "assistant",
                    full_response
                )

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)

            # Show error in chat
            error_message = Message(role="system", content=error_msg)
            self.after(0, lambda: self.chat_panel.add_message(error_message))

        finally:
            self.is_generating = False
            self.after(0, lambda: self.input_panel.set_sending_state(False))
            self.after(0, lambda: self.input_panel.focus_input())

    def _stop_generation_callback(self) -> None:
        """Stop the current generation."""
        self._stop_generation = True

    def _on_closing(self) -> None:
        """Handle window closing event."""
        # Save window size
        self.settings.set("window_width", self.winfo_width())
        self.settings.set("window_height", self.winfo_height())

        # Close window
        self.destroy()

    def run(self) -> None:
        """Start the application main loop."""
        self.mainloop()
