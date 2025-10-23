"""
Ollama API integration service.
"""
from typing import List, Optional, Iterator, Dict, Any
import ollama


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self) -> None:
        """Initialize the Ollama service."""
        self.client = ollama.Client()

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available Ollama models.

        Returns:
            List of model information dictionaries.

        Raises:
            Exception: If unable to connect to Ollama.
        """
        try:
            response = self.client.list()
            # Response is a ListResponse object with a 'models' attribute
            models = []
            for model in response.get('models', []):
                # Convert Model object to dictionary
                models.append({
                    "name": model.model,  # model.model contains the name
                    "size": model.size,
                    "modified_at": str(model.modified_at) if model.modified_at else None,
                    "digest": model.digest,
                })
            return models
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")

    def send_message(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str] | Dict[str, Any]:
        """
        Send a message to Ollama and get response.

        Args:
            model: The model name to use.
            messages: List of message dictionaries with 'role' and 'content'.
            stream: Whether to stream the response.
            temperature: Controls randomness (0.0-2.0). Higher = more random.
            top_p: Nucleus sampling threshold (0.0-1.0).
            top_k: Limits token selection to top k tokens.
            max_tokens: Maximum tokens to generate (num_predict in Ollama).

        Returns:
            Iterator of response chunks if streaming, else full response dict.

        Raises:
            Exception: If the API call fails.
        """
        try:
            # Build options dictionary for model parameters
            options = {}
            if temperature is not None:
                options["temperature"] = temperature
            if top_p is not None:
                options["top_p"] = top_p
            if top_k is not None:
                options["top_k"] = top_k
            if max_tokens is not None:
                options["num_predict"] = max_tokens  # Ollama uses num_predict

            response = self.client.chat(
                model=model,
                messages=messages,
                stream=stream,
                options=options if options else None,
            )

            if stream:
                return self._stream_response(response)
            else:
                return response

        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")

    def _stream_response(self, response: Iterator) -> Iterator[str]:
        """
        Process streaming response from Ollama.

        Args:
            response: The streaming response from Ollama.

        Yields:
            Response content chunks.
        """
        for chunk in response:
            # Chunk is a ChatResponse object with a 'message' attribute
            if hasattr(chunk, 'message') and chunk.message:
                content = chunk.message.content
                if content:  # Only yield non-empty content
                    yield content

    def check_connection(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            True if Ollama is accessible, False otherwise.
        """
        try:
            self.list_models()
            return True
        except Exception:
            return False

    def unload_model(self, model: str) -> None:
        """
        Unload a model from VRAM to free up resources.

        This sends a request with keep_alive=0 to immediately unload the model.

        Args:
            model: The model name to unload.
        """
        try:
            # Generate with keep_alive=0 tells Ollama to immediately unload
            self.client.generate(
                model=model,
                prompt="",
                keep_alive=0
            )
        except Exception:
            # Silently fail - model may already be unloaded or not loaded
            pass

    def cleanup(self, current_model: Optional[str] = None) -> None:
        """
        Clean up resources and unload models from VRAM.

        Args:
            current_model: The currently active model to unload (optional).
        """
        if current_model:
            self.unload_model(current_model)
