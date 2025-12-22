from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""

    @abstractmethod
    async def generate_audio(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """
        Generate audio from text.

        Args:
            text: The text to convert to speech.
            voice_id: The ID of the voice to use.
            **kwargs: Additional provider-specific arguments.

        Returns:
            The generated audio as bytes.
        """
        pass
