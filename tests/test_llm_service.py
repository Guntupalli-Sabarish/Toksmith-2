"""
Unit tests for the LLM Service module.

Tests cover script generation, Gemini client, and model validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.llm_service import LLMService, RawThreadData
from app.services.llm_service.gemini_client import GeminiClient, GeminiRequest, GeminiResponse
from app.models.script import Script, DialogueLine


class TestDialogueLine:
    """Tests for DialogueLine model."""
    
    def test_create_dialogue_line(self):
        """Test creating a dialogue line."""
        line = DialogueLine(
            speaker="Narrator",
            text="Welcome to the show",
            audio_file_path="/path/to/audio.wav",
            start_time=0.0,
            duration=3.5
        )
        
        assert line.speaker == "Narrator"
        assert line.text == "Welcome to the show"
        assert line.audio_file_path == "/path/to/audio.wav"
        assert line.start_time == 0.0
        assert line.duration == 3.5
    
    def test_dialogue_line_defaults(self):
        """Test dialogue line with default values."""
        line = DialogueLine(
            speaker="OP",
            text="This is my story"
        )
        
        assert line.speaker == "OP"
        assert line.text == "This is my story"
        assert line.audio_file_path == ""
        assert line.start_time == 0.0
        assert line.duration == 0.0


class TestScript:
    """Tests for Script model."""
    
    def test_create_script(self):
        """Test creating a script."""
        lines = [
            DialogueLine(speaker="Narrator", text="Line 1"),
            DialogueLine(speaker="OP", text="Line 2")
        ]
        
        script = Script.create(
            lines=lines,
            background="minecraft-parkour",
            characters=["narrator", "op"]
        )
        
        assert script.id.startswith("script_")
        assert len(script.lines) == 2
        assert script.background == "minecraft-parkour"
        assert script.characters == ["narrator", "op"]
    
    def test_add_dialogue_line(self):
        """Test adding a dialogue line to script."""
        script = Script.create(
            lines=[DialogueLine(speaker="Narrator", text="Line 1")],
            background="minecraft-parkour"
        )
        
        new_line = DialogueLine(speaker="OP", text="Line 2")
        script.add_dialogue_line(new_line)
        
        assert len(script.lines) == 2
        assert script.lines[1].speaker == "OP"
    
    def test_update_audio_path(self):
        """Test updating audio path for a line."""
        script = Script.create(
            lines=[
                DialogueLine(speaker="Narrator", text="Line 1"),
                DialogueLine(speaker="OP", text="Line 2")
            ],
            background="minecraft-parkour"
        )
        
        script.update_audio_path(0, "/path/to/audio1.wav")
        
        assert script.lines[0].audio_file_path == "/path/to/audio1.wav"
        assert script.lines[1].audio_file_path == ""


class TestGeminiClient:
    """Tests for GeminiClient."""
    
    def test_gemini_client_init(self):
        """Test Gemini client initialization."""
        client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash-exp")
        
        assert client.api_key == "test-key"
        assert client.model_name == "gemini-2.0-flash-exp"
    
    def test_gemini_client_no_api_key(self):
        """Test that client raises error without API key."""
        with pytest.raises(ValueError, match="Gemini API key is required"):
            GeminiClient(api_key="")


class TestLLMService:
    """Tests for LLMService."""
    
    def test_llm_service_init_with_api_key(self):
        """Test LLM service initialization with API key."""
        service = LLMService(api_key="test-key", model="gemini-2.0-flash-exp")
        assert service.gemini_client.api_key == "test-key"
    
    def test_llm_service_init_no_api_key(self):
        """Test LLM service raises error without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Gemini API key is required"):
                LLMService()
    
    def test_validate_response_valid(self):
        """Test validation of valid response."""
        service = LLMService(api_key="test-key")
        
        valid_response = {
            "lines": [
                {"speaker": "Narrator", "text": "Hello"},
                {"speaker": "OP", "text": "World"}
            ],
            "background": "minecraft-parkour",
            "characters": ["narrator", "op"]
        }
        
        assert service._validate_response(valid_response) is True
    
    def test_validate_response_invalid(self):
        """Test validation of invalid responses."""
        service = LLMService(api_key="test-key")
        
        # Not a dict
        assert service._validate_response("invalid") is False
        
        # No lines
        assert service._validate_response({}) is False
        
        # Lines not an array
        assert service._validate_response({"lines": "not-an-array"}) is False
        
        # Line missing speaker
        assert service._validate_response({
            "lines": [{"text": "no speaker"}]
        }) is False
        
        # Line missing text
        assert service._validate_response({
            "lines": [{"speaker": "no text"}]
        }) is False
    
    def test_build_prompt(self):
        """Test prompt building."""
        service = LLMService(api_key="test-key")
        
        raw_thread = RawThreadData(
            title="Test Thread",
            content="Content here",
            author="test_user",
            subreddit="test",
            upvotes=100,
            comments=[
                {"author": "user1", "content": "Comment 1", "upvotes": 50},
                {"author": "user2", "content": "Comment 2", "upvotes": 30}
            ]
        )
        
        prompt = service._build_prompt(raw_thread)
        
        assert "Test Thread" in prompt
        assert "Content here" in prompt
        assert "test_user" in prompt
        assert "r/test" in prompt
        assert "Comment 1" in prompt
        assert "Comment 2" in prompt
        assert "JSON" in prompt
    
    @pytest.mark.asyncio
    async def test_generate_script_with_mock_response(self):
        """Test script generation with mocked LLM response."""
        service = LLMService(api_key="test-key")
        
        # Mock the LLM call
        mock_response = GeminiResponse(
            content='{"lines": [{"speaker": "Narrator", "text": "Test line"}], "background": "minecraft-parkour", "characters": ["narrator"]}'
        )
        
        with patch.object(service, '_call_llm', return_value=mock_response):
            raw_thread = RawThreadData(
                title="Test",
                content="Content",
                author="user",
                subreddit="test",
                upvotes=100,
                comments=[]
            )
            
            script = await service.generate_structured_script(raw_thread)
            
            assert isinstance(script, Script)
            assert len(script.lines) == 1
            assert script.lines[0].speaker == "Narrator"
            assert script.lines[0].text == "Test line"


class TestRawThreadData:
    """Tests for RawThreadData."""
    
    def test_create_raw_thread_data(self):
        """Test creating RawThreadData."""
        thread = RawThreadData(
            title="Test Title",
            content="Test content",
            author="test_user",
            subreddit="test",
            upvotes=100,
            comments=[
                {"author": "user1", "content": "Comment", "upvotes": 50}
            ]
        )
        
        assert thread.title == "Test Title"
        assert thread.content == "Test content"
        assert thread.author == "test_user"
        assert thread.subreddit == "test"
        assert thread.upvotes == 100
        assert len(thread.comments) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
