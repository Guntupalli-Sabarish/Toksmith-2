"""Script entity model for dialogue-based video scripts."""

from typing import List, Optional
from pydantic import BaseModel, Field
import time
import random
import string


class DialogueLine(BaseModel):
    """Represents a single line of dialogue in the script."""
    speaker: str = Field(..., description="The speaker of the line (e.g., Narrator, OP, Commenter1)")
    text: str = Field(..., description="The dialogue text")
    audio_file_path: str = Field(default="", description="Path to the generated audio file")
    start_time: float = Field(default=0.0, description="Start time in the video timeline")
    duration: float = Field(default=0.0, description="Duration of the audio clip")


class Script(BaseModel):
    """Represents a complete video script."""
    id: str = Field(..., description="Unique identifier for the script")
    lines: List[DialogueLine] = Field(default_factory=list, description="List of dialogue lines")
    background: str = Field(default="minecraft-parkour", description="Background video template")
    characters: List[str] = Field(default_factory=list, description="List of character names used")

    @classmethod
    def create(
        cls,
        lines: List[DialogueLine],
        background: str = "minecraft-parkour",
        characters: Optional[List[str]] = None
    ) -> "Script":
        """Create a new Script entity with auto-generated ID."""
        script_id = cls.generate_id()
        return cls(
            id=script_id,
            lines=lines,
            background=background,
            characters=characters or []
        )

    @staticmethod
    def generate_id() -> str:
        """Generate a unique script ID."""
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"script_{timestamp}_{random_str}"

    def add_dialogue_line(self, line: DialogueLine) -> "Script":
        """Add a new dialogue line to the script."""
        self.lines.append(line)
        return self

    def update_audio_path(self, line_index: int, audio_file_path: str) -> "Script":
        """Update the audio file path for a specific line."""
        if 0 <= line_index < len(self.lines):
            self.lines[line_index].audio_file_path = audio_file_path
        return self

    def to_dict(self) -> dict:
        """Convert script to dictionary."""
        return self.model_dump()

    class Config:
        json_schema_extra = {
            "example": {
                "id": "script_1234567890_abc123def",
                "lines": [
                    {
                        "speaker": "Narrator",
                        "text": "Welcome to today's Reddit story...",
                        "audio_file_path": "/path/to/audio1.wav",
                        "start_time": 0.0,
                        "duration": 3.5
                    }
                ],
                "background": "minecraft-parkour",
                "characters": ["narrator", "op", "commenter1"]
            }
        }
