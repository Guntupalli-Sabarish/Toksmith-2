import os
import uuid
from typing import Optional, List, Tuple
from app.models.script import Script
from .providers.base import TTSProvider
from .providers.hume_provider import HumeTTSProvider

class TTSService:
    """Service for generating audio from scripts using TTS providers."""

    def __init__(self, provider: Optional[TTSProvider] = None):
        self.provider = provider or HumeTTSProvider()

    async def generate_audio_for_text(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate audio for a single text string.
        
        Args:
            text: The text to convert to speech.
            voice_id: Optional voice ID to use.
            
        Returns:
            Audio bytes (MP3).
        """
        return await self.provider.generate_audio(text=text, voice_id=voice_id)

    async def generate_script_audio_bytes(self, script: Script) -> List[Tuple[int, bytes, str]]:
        """
        Generate audio bytes for all lines in the script.
        
        Args:
            script: The script to generate audio for.
            
        Returns:
            List of tuples: (line_index, audio_bytes, filename)
        """
        results = []
        
        for i, line in enumerate(script.lines):
            try:
                # Generate audio
                audio_bytes = await self.provider.generate_audio(
                    text=line.text,
                    voice_id=None 
                )
                
                # Generate filename
                filename = f"{script.id}_{i}_{uuid.uuid4().hex[:8]}.mp3"
                results.append((i, audio_bytes, filename))
                
            except Exception as e:
                print(f"Failed to generate audio for line {i}: {e}")
                # Continue to try other lines even if one fails
                
        return results

    async def generate_script_audio(self, script: Script, output_dir: str = "static/audio") -> Script:
        """
        Generate audio for all lines in the script and save locally.
        (Legacy method for backwards compatibility)

        Args:
            script: The script to generate audio for.
            output_dir: Directory to save audio files.

        Returns:
            Updated script with audio file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = await self.generate_script_audio_bytes(script)
        
        for line_index, audio_bytes, filename in results:
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            
            script.update_audio_path(line_index, filepath)
                
        return script


def get_tts_service() -> TTSService:
    """Dependency injection for TTS service."""
    return TTSService()
