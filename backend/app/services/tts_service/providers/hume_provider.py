import os
import base64
from typing import Optional
from hume import AsyncHumeClient
from hume.tts import PostedUtterance, PostedUtteranceVoiceWithName
from app.core.config import settings
from .base import TTSProvider

class HumeTTSProvider(TTSProvider):
    """Hume AI implementation of TTS Provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.hume_api_key
        if not self.api_key:
            raise ValueError("Hume API key is required. Set HUME_API_KEY environment variable.")
        self.client = AsyncHumeClient(api_key=self.api_key)

    async def generate_audio(self, text: str, voice_id: Optional[str] = None, **kwargs) -> bytes:
        """
        Generate audio using Hume AI.

        Args:
            text: Text to synthesize
            voice_id: Name of the voice to use (defaults to 'Ava Song')
            **kwargs: 
                provider: 'HUME_AI' (default) or 'CUSTOM_VOICE'
        
        Returns:
            Audio bytes (MP3/WAV depending on Hume default, usually MP3)
        """
        voice_name = voice_id or "Ava Song"
        provider = kwargs.get("provider", "HUME_AI")

        utterance = PostedUtterance(
            text=text,
            voice=PostedUtteranceVoiceWithName(name=voice_name, provider=provider)
        )

        try:
            response = await self.client.tts.synthesize_json(
                utterances=[utterance]
            )

            if not response.generations:
                raise Exception("No generations returned from Hume API")

            # Return the first generation's audio
            return base64.b64decode(response.generations[0].audio)

        except Exception as e:
            print(f"Error generating audio with Hume: {e}")
            raise
