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
            return response.get("models", [])
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")

    def send_message(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
    ) -> Iterator[str] | Dict[str, Any]:
        """
        Send a message to Ollama and get response.

        Args:
            model: The model name to use.
            messages: List of message dictionaries with 'role' and 'content'.
            stream: Whether to stream the response.

        Returns:
            Iterator of response chunks if streaming, else full response dict.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = self.client.chat(
                model=model,
                messages=messages,
                stream=stream,
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
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]

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
