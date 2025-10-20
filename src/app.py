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
        super().__init__(className="OL-GUI")

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

        # Apply saved font size
        font_size = self.settings.get("font_size", 14)
        self._apply_font_size(font_size)

        # Load initial data
        self._load_initial_data()

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
                # Load image with PIL
                img = Image.open(icon_path).convert('RGBA')

                # Convert to PPM format in memory
                with io.BytesIO() as output:
                    img.save(output, format='PPM')
                    ppm_data = output.getvalue()

                # Create PhotoImage from PPM data
                self._icon_photo = tk.PhotoImage(data=ppm_data)

                # Set as window icon (for dock/taskbar on Linux)
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
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # Save window size on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Initialize sidebar width
        self.sidebar_width = self.settings.get("sidebar_width", 350)

        # Configure grid - control column widths directly
        self.grid_columnconfigure(0, weight=0, minsize=self.sidebar_width)  # Sidebar - controlled width
        self.grid_columnconfigure(1, weight=0, minsize=4)  # Separator - 4px
        self.grid_columnconfigure(2, weight=1)  # Chat/Input - expandable
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
        self.sidebar.set_settings_callback(self._on_settings)
        self.sidebar.set_rename_conversation_callback(self._on_rename_conversation)

        # Resize separator
        self.separator = ctk.CTkFrame(self, width=4, fg_color=("#cccccc", "#444444"), cursor="sb_h_double_arrow")
        self.separator.grid(row=0, column=1, rowspan=2, sticky="ns")
        self.separator.bind("<Button-1>", self._start_resize)
        self.separator.bind("<B1-Motion>", self._do_resize)

        # Chat panel (with saved font size)
        font_size = self.settings.get("font_size", 14)
        self.chat_panel = ChatPanel(self, font_size=font_size)
        self.chat_panel.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)

        # Input panel
        self.input_panel = InputPanel(
            self,
            on_send=self._on_send_message,
        )
        self.input_panel.grid(row=1, column=2, sticky="ew", padx=0, pady=0)
        self.input_panel.set_stop_callback(self._stop_generation_callback)

        # Bind window resize to constrain sidebar
        self.bind("<Configure>", self._on_window_resize)

    def _load_initial_data(self) -> None:
        """Load initial data (models, conversations)."""
        # Load models in background
        threading.Thread(target=self._refresh_models, daemon=True).start()

        # Load conversation history
        conversations = self._load_conversations()

        # Load most recent conversation, or create new one if none exist
        if conversations:
            # Load the most recent conversation (first in the list, sorted by updated_at DESC)
            most_recent = conversations[0]
            self._on_conversation_select(most_recent.id)
        else:
            # No conversations exist, create a new one
            self._on_new_conversation()

        # Recalculate message bubble heights after window is fully rendered
        self.after(100, self._recalculate_message_heights)

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

    def _load_conversations(self):
        """
        Load conversation history into sidebar.

        Returns:
            List of conversations, or empty list if loading fails.
        """
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
        """
        Handle model selection change.

        Args:
            model_name: Selected model name.
        """
        # Unload previous model from VRAM before switching
        if self.current_model and self.current_model != model_name:
            self.ollama.cleanup(self.current_model)

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

            # Reload conversations to keep sorted order (most recent first)
            self._load_conversations()

            # Set the new conversation as current in sidebar
            self.sidebar._handle_conversation_click(conv.id)

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
                # Unload previous model if switching to a different one
                if self.current_model and self.current_model != conv.model:
                    self.ollama.cleanup(self.current_model)

                self.current_conversation = conv
                self.current_model = conv.model

                # Update UI
                self.chat_panel.load_messages(conv.messages)
                self.sidebar.model_dropdown.set(conv.model)

        except Exception as e:
            print(f"Failed to load conversation: {e}")

    def _on_rename_conversation(self, conv_id: int, new_title: str) -> None:
        """
        Handle conversation rename.

        Args:
            conv_id: Conversation ID to rename.
            new_title: New title for the conversation.
        """
        try:
            # Update in database
            self.conv_manager.rename_conversation(conv_id, new_title)

            # Update UI
            self.sidebar.update_conversation_title(conv_id, new_title)

            # Update current conversation title if it's the one being renamed
            if self.current_conversation and self.current_conversation.id == conv_id:
                self.current_conversation.title = new_title

        except Exception as e:
            print(f"Failed to rename conversation: {e}")

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

        # Hidden commands
        command = message_text.strip().lower()

        if command == "/test-system":
            # Test system message colors
            system_message = Message(role="system", content="This is a test system message. System messages are used for errors and notifications.")
            self.chat_panel.add_message(system_message)
            return

        elif command == "/bye" or command == "/quit" or command == "/exit":
            # Quit the application
            system_message = Message(role="system", content="Goodbye! Closing application...")
            self.chat_panel.add_message(system_message)
            self.after(1000, self._on_closing)  # Close after 1 second
            return

        elif command == "/clear":
            # Clear current conversation
            self.chat_panel.clear_messages()
            system_message = Message(role="system", content="Conversation cleared.")
            self.chat_panel.add_message(system_message)
            return

        elif command == "/help":
            # Show help message
            help_text = """Available hidden commands:
/help - Show this help message
/test-system - Test system message colors
/clear - Clear current conversation
/bye, /quit, /exit - Close the application"""
            system_message = Message(role="system", content=help_text)
            self.chat_panel.add_message(system_message)
            return

        # Create user message
        user_message = Message(role="user", content=message_text)

        # Add to UI
        self.chat_panel.add_message(user_message)

        # Save to database (if auto-save enabled)
        if self.current_conversation and self.settings.get("auto_save", True):
            self.conv_manager.add_message(
                self.current_conversation.id,
                "user",
                message_text
            )
            # Reload conversations to update sort order (most recent first)
            conversations = self._load_conversations()
            # Re-select current conversation to maintain UI state
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
            # Start streaming message with thinking animation
            self.after(0, lambda: self.chat_panel.start_streaming_message("assistant"))

            # Start thinking animation
            thinking_animation_running = [True]  # Use list to allow modification in nested function
            thinking_dots = [0]

            def animate_thinking():
                if not thinking_animation_running[0]:
                    return
                dots = "." * (thinking_dots[0] + 1)
                self.after(0, lambda: self.chat_panel.update_streaming_message(f"Thinking{dots}"))
                thinking_dots[0] = (thinking_dots[0] + 1) % 3
                if thinking_animation_running[0]:
                    threading.Timer(0.5, animate_thinking).start()

            animate_thinking()

            # Get message history
            messages = []
            if self.current_conversation:
                conv = self.conv_manager.get_conversation(self.current_conversation.id)
                if conv:
                    messages = conv.get_message_history()

            # Get response (streaming or non-streaming based on setting)
            full_response = ""
            use_streaming = self.settings.get("stream_responses", True)

            if use_streaming:
                # Streaming mode
                response_stream = self.ollama.send_message(
                    self.current_model,
                    messages,
                    stream=True
                )

                for chunk in response_stream:
                    if self._stop_generation:
                        break

                    # Stop thinking animation on first chunk
                    if not full_response:
                        thinking_animation_running[0] = False

                    full_response += chunk
                    # Update UI in main thread
                    self.after(0, lambda r=full_response: self.chat_panel.update_streaming_message(r))

                # Finish streaming
                self.after(0, lambda: self.chat_panel.finish_streaming_message())
            else:
                # Non-streaming mode - get full response at once
                response = self.ollama.send_message(
                    self.current_model,
                    messages,
                    stream=False
                )

                # Stop thinking animation
                thinking_animation_running[0] = False

                # Response is a ChatResponse object with message attribute
                if hasattr(response, 'message'):
                    full_response = response.message.content if response.message else ""
                elif isinstance(response, dict) and 'message' in response:
                    full_response = response['message'].get('content', '')

                # Add the complete message to UI
                assistant_message = Message(role="assistant", content=full_response)
                self.after(0, lambda: self.chat_panel.add_message(assistant_message))

            # Save assistant message to database (if auto-save enabled)
            if self.current_conversation and full_response and self.settings.get("auto_save", True):
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

    def _on_settings(self) -> None:
        """Open the settings dialog."""
        from components.settings_dialog import SettingsDialog

        dialog = SettingsDialog(
            self,
            self.settings,
            on_save=self._on_settings_saved
        )

    def _on_settings_saved(self) -> None:
        """Handle settings being saved."""
        # Apply theme change
        theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        # Update all components with new theme colors
        self._apply_theme_colors(theme)

        # Apply font size changes
        font_size = self.settings.get("font_size", 14)
        self._apply_font_size(font_size)

    def _apply_theme_colors(self, theme: str) -> None:
        """
        Apply theme colors to all components.

        Args:
            theme: Theme name ("dark", "light", or "system")
        """
        # Update all components
        self.sidebar.update_theme(theme)
        self.chat_panel.update_theme(theme)
        self.input_panel.update_theme(theme)

    def _start_resize(self, event) -> None:
        """Handle start of sidebar resize."""
        self._resize_start_x = event.x_root

    def _do_resize(self, event) -> None:
        """Handle sidebar resize dragging."""
        # Calculate new width based on mouse position
        # Use absolute position relative to window start
        mouse_x = event.x_root - self.winfo_rootx()

        # Apply constraints
        min_width = 300
        max_width = self.winfo_width() // 2

        new_width = max(min_width, min(mouse_x, max_width))

        # Update sidebar width by configuring the grid column
        self.sidebar_width = new_width
        self.grid_columnconfigure(0, minsize=new_width)

    def _on_window_resize(self, event) -> None:
        """Handle window resize to constrain sidebar width."""
        if event.widget == self:
            # Check if sidebar exceeds max allowed width
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
        """
        Apply font size to all components.

        Args:
            font_size: Font size in pixels
        """
        # Update sidebar
        if hasattr(self.sidebar, 'update_font_size'):
            self.sidebar.update_font_size(font_size)

        # Update input panel text box
        if hasattr(self.input_panel, 'input_text'):
            self.input_panel.input_text.configure(font=("", font_size))

        # Update chat panel font size (for new messages)
        if hasattr(self.chat_panel, 'font_size'):
            self.chat_panel.font_size = font_size

        # Update existing message bubbles
        if hasattr(self.chat_panel, 'message_widgets'):
            for bubble in self.chat_panel.message_widgets:
                bubble.update_font_size(font_size)

    def _on_closing(self) -> None:
        """Handle window closing event."""
        # Save window size and sidebar width
        self.settings.set("window_width", self.winfo_width())
        self.settings.set("window_height", self.winfo_height())
        self.settings.set("sidebar_width", self.sidebar_width)

        # Unload current model from VRAM
        if self.current_model:
            self.ollama.cleanup(self.current_model)

        # Close window
        self.destroy()

    def run(self) -> None:
        """Start the application main loop."""
        self.mainloop()
