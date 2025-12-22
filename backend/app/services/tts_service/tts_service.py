import os
import uuid
from typing import Optional
from app.models.script import Script
from .providers.base import TTSProvider
from .providers.hume_provider import HumeTTSProvider

class TTSService:
    """Service for generating audio from scripts using TTS providers."""

    def __init__(self, provider: Optional[TTSProvider] = None):
        self.provider = provider or HumeTTSProvider()

    async def generate_script_audio(self, script: Script, output_dir: str = "static/audio") -> Script:
        """
        Generate audio for all lines in the script.

        Args:
            script: The script to generate audio for.
            output_dir: Directory to save audio files.

        Returns:
            Updated script with audio file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i, line in enumerate(script.lines):
            # Skip if audio already exists
            if line.audio_file_path and os.path.exists(line.audio_file_path):
                continue

            try:
                # Generate audio
                # TODO: Implement better speaker-to-voice mapping
                # For now, we rely on the provider's default voice
                audio_bytes = await self.provider.generate_audio(
                    text=line.text,
                    voice_id=None 
                )
                
                # Save to file
                filename = f"{script.id}_{i}_{uuid.uuid4().hex[:8]}.mp3"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)
                
                # Update script
                script.update_audio_path(i, filepath)
                
            except Exception as e:
                print(f"Failed to generate audio for line {i}: {e}")
                # We continue to try other lines even if one fails
                
        return script


def get_tts_service() -> TTSService:
    """Dependency injection for TTS service."""
    return TTSService()
