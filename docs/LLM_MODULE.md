# LLM Script Generator Module

## Overview

The LLM Script Generator is a modular service within the TokSmith project that transforms raw content (Reddit threads, Twitter posts, etc.) into structured, dialogue-based video scripts suitable for short-form video creation.

## 🎯 Purpose

This module focuses **exclusively** on script generation using Large Language Models (LLMs). It takes unstructured content and converts it into a format ready for Text-to-Speech (TTS) and video assembly.

## 📁 Project Structure

```
Toksmith/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── script.py              # Script and DialogueLine models
│   └── services/
│       └── llm_service/
│           ├── __init__.py         # Package exports
│           ├── gemini_client.py    # Gemini API wrapper
│           ├── llm_service.py      # Main service logic
│           └── README.md           # Detailed documentation
├── examples/
│   └── llm_service_example.py     # Usage example
├── tests/
│   └── test_llm_service.py        # Unit tests
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── LLM_MODULE.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Run the Example

```bash
# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Run the example
python examples/llm_service_example.py
```

## 💡 Usage Example

```python
import asyncio
from app.services.llm_service import LLMService, RawThreadData

async def main():
    # Initialize service
    llm_service = LLMService()
    
    # Prepare input data
    raw_thread = RawThreadData(
        title="AITA for refusing to give my mother money?",
        content="My grandmother passed away and left me $50,000...",
        author="throwaway12345",
        subreddit="AmItheAsshole",
        upvotes=15420,
        comments=[
            {
                "author": "RedditUser1",
                "content": "NTA. That was YOUR inheritance...",
                "upvotes": 8234
            }
        ]
    )
    
    # Generate script
    script = await llm_service.generate_structured_script(raw_thread)
    
    # Use the generated script
    print(f"Script ID: {script.id}")
    print(f"Total lines: {len(script.lines)}")
    
    for line in script.lines:
        print(f"{line.speaker}: {line.text}")

asyncio.run(main())
```

## 📊 Data Flow

```
Raw Content (Reddit/Twitter)
         ↓
   RawThreadData
         ↓
    LLMService.generate_structured_script()
         ↓
   Gemini API Call
         ↓
   JSON Response
         ↓
   Parse & Validate
         ↓
   Script Entity
         ↓
  (Ready for TTS)
```

## 🔑 Key Components

### 1. **Script Model** (`app/models/script.py`)

Defines the structure of video scripts:

- **DialogueLine**: Single line of dialogue with speaker, text, and audio metadata
- **Script**: Complete script with multiple lines, background info, and characters

### 2. **Gemini Client** (`app/services/llm_service/gemini_client.py`)

Low-level wrapper for Google's Gemini API:

- Handles HTTP requests to Gemini
- Manages authentication
- Provides token usage estimation
- Error handling and retry logic

### 3. **LLM Service** (`app/services/llm_service/llm_service.py`)

High-level service orchestrating script generation:

- Builds prompts from raw content
- Calls Gemini API
- Parses and validates responses
- Provides fallback mock scripts
- Creates structured Script entities

## 🎬 Generated Script Format

Scripts are generated with the following structure:

```json
{
  "id": "script_1234567890_abc123def",
  "lines": [
    {
      "speaker": "Narrator",
      "text": "Welcome to another episode of Reddit Stories...",
      "audio_file_path": "",
      "start_time": 0,
      "duration": 0
    },
    {
      "speaker": "OP",
      "text": "My grandmother passed away 5 years ago...",
      "audio_file_path": "",
      "start_time": 0,
      "duration": 0
    },
    {
      "speaker": "Commenter1",
      "text": "NTA. That was YOUR inheritance...",
      "audio_file_path": "",
      "start_time": 0,
      "duration": 0
    }
  ],
  "background": "minecraft-parkour",
  "characters": ["narrator", "op", "commenter1", "commenter2"]
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | None | Yes |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.0-flash-exp` | No |

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## 🧪 Testing

Run the unit tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/test_llm_service.py -v
```

Test coverage includes:
- Model validation
- Script creation and manipulation
- Gemini client functionality
- LLM service orchestration
- Response parsing and validation
- Error handling and fallbacks

## 📈 Features

### ✅ Implemented

- ✅ Gemini API integration
- ✅ Structured script generation
- ✅ Multi-speaker dialogue support
- ✅ JSON response parsing
- ✅ Validation and error handling
- ✅ Fallback mock scripts
- ✅ Type-safe Pydantic models
- ✅ Async/await support
- ✅ Comprehensive documentation
- ✅ Unit tests
- ✅ Usage examples

### 🔮 Future Enhancements

- [ ] Support for other LLM providers (OpenAI, Anthropic)
- [ ] Caching for repeated content
- [ ] Batch processing support
- [ ] Custom prompt templates
- [ ] Script editing and refinement
- [ ] Multi-language support
- [ ] Tone and style customization
- [ ] Integration with other content sources

## 🤝 Integration Points

This module integrates with other TokSmith services:

1. **Input Service** → Provides raw content data
2. **TTS Service** ← Receives script for audio generation
3. **Video Service** ← Uses completed scripts with audio for video assembly
4. **Storage Service** ← Stores generated scripts

## 📝 Best Practices

1. **Environment Variables**: Always use `.env` file, never commit API keys
2. **Error Handling**: Wrap service calls in try-except blocks
3. **Async Operations**: Always use `await` with service methods
4. **Type Safety**: Use type hints and Pydantic models
5. **Testing**: Write tests for new functionality
6. **Documentation**: Keep docs updated with code changes



## 🐛 Troubleshooting

### "Gemini API key is required"
- Ensure `GEMINI_API_KEY` is set in your environment
- Check `.env` file exists and is loaded
- Verify API key is valid

### "Failed to parse script from LLM response"
- Check Gemini API quota and limits
- Verify network connectivity
- Review LLM response in logs

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+)
- Verify virtual environment is activated

