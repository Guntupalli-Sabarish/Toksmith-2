# LLM Service Architecture Diagrams

## High-Level Module Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      TokSmith Application                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐     ┌────────────────┐     ┌──────────────┐│
│  │  Input Service │────►│  LLM Service   │────►│ TTS Service  ││
│  │                │     │                │     │              ││
│  │  - Reddit      │     │  - Script Gen  │     │ - Audio Gen  ││
│  │  - Twitter     │     │  - Gemini AI   │     │              ││
│  │  - Custom      │     │  - Validation  │     │              ││
│  └────────────────┘     └────────────────┘     └──────────────┘│
│                                                        │          │
│                                                        ▼          │
│  ┌────────────────┐                          ┌──────────────┐   │
│  │ Storage Service│◄─────────────────────────│Video Service │   │
│  │                │                          │              │   │
│  │  - S3/MinIO    │                          │ - Assembly   │   │
│  │  - Scripts     │                          │ - Rendering  │   │
│  │  - Videos      │                          │              │   │
│  └────────────────┘                          └──────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## LLM Service Internal Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Service Module                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 LLMService (Main)                     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │  • generate_structured_script()                       │  │
│  │  • _build_prompt()                                    │  │
│  │  • _parse_script_response()                           │  │
│  │  • _validate_response()                               │  │
│  │  • _generate_mock_script()                            │  │
│  │                                                        │  │
│  └───────────────┬────────────────────────────┬──────────┘  │
│                  │                            │              │
│                  ▼                            ▼              │
│  ┌──────────────────────────┐   ┌──────────────────────┐   │
│  │    GeminiClient          │   │   Models             │   │
│  ├──────────────────────────┤   ├──────────────────────┤   │
│  │                          │   │                      │   │
│  │ • generate_content()     │   │ • Script             │   │
│  │ • _estimate_tokens()     │   │ • DialogueLine       │   │
│  │                          │   │ • RawThreadData      │   │
│  │                          │   │                      │   │
│  └──────────┬───────────────┘   └──────────────────────┘   │
│             │                                                │
│             ▼                                                │
│  ┌─────────────────────┐                                    │
│  │   Gemini API        │                                    │
│  │   (External)        │                                    │
│  └─────────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

```
┌────────┐         ┌──────────┐         ┌─────────┐         ┌────────┐
│ Client │         │   LLM    │         │ Gemini  │         │ Script │
│        │         │ Service  │         │ Client  │         │ Entity │
└───┬────┘         └────┬─────┘         └────┬────┘         └───┬────┘
    │                   │                    │                   │
    │ RawThreadData     │                    │                   │
    │──────────────────►│                    │                   │
    │                   │                    │                   │
    │                   │ Build Prompt       │                   │
    │                   │───────────┐        │                   │
    │                   │           │        │                   │
    │                   │◄──────────┘        │                   │
    │                   │                    │                   │
    │                   │ GeminiRequest      │                   │
    │                   │───────────────────►│                   │
    │                   │                    │                   │
    │                   │                    │ HTTP POST         │
    │                   │                    │──────────┐        │
    │                   │                    │          │        │
    │                   │                    │◄─────────┘        │
    │                   │                    │                   │
    │                   │  GeminiResponse    │                   │
    │                   │◄───────────────────│                   │
    │                   │                    │                   │
    │                   │ Parse & Validate   │                   │
    │                   │───────────┐        │                   │
    │                   │           │        │                   │
    │                   │◄──────────┘        │                   │
    │                   │                    │                   │
    │                   │ Create Script      │                   │
    │                   │───────────────────────────────────────►│
    │                   │                    │                   │
    │      Script       │                    │                   │
    │◄──────────────────│                    │                   │
    │                   │                    │                   │
```

## Script Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Script Generation Pipeline                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Raw Thread Data │
                    │                  │
                    │  • Title         │
                    │  • Content       │
                    │  • Comments      │
                    │  • Metadata      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Build Prompt    │
                    │                  │
                    │  • Context       │
                    │  • Instructions  │
                    │  • Format Spec   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Gemini API Call │
                    │                  │
                    │  • max_tokens    │
                    │  • temperature   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Parse Response  │
                    │                  │
                    │  • Clean JSON    │
                    │  • Remove markup │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Validate        │
                    │                  │
                    │  • Structure     │
                    │  • Required keys │
                    └────────┬─────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
          ┌─────────────┐    ┌──────────────┐
          │   Success   │    │   Failure    │
          │             │    │              │
          │ Create      │    │ Generate     │
          │ Script      │    │ Mock Script  │
          │ Entity      │    │              │
          └──────┬──────┘    └──────┬───────┘
                 │                  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │ Script Entity  │
                 │                │
                 │ • ID           │
                 │ • Lines[]      │
                 │ • Background   │
                 │ • Characters[] │
                 └────────────────┘
```

## Model Relationships

```
┌────────────────────────────────────────────────┐
│                   Script                       │
├────────────────────────────────────────────────┤
│ + id: str                                      │
│ + lines: List[DialogueLine]                   │
│ + background: str                              │
│ + characters: List[str]                        │
├────────────────────────────────────────────────┤
│ + create(lines, bg, chars): Script             │
│ + add_dialogue_line(line): Script              │
│ + update_audio_path(idx, path): Script         │
│ + to_dict(): dict                              │
└───────────────────┬────────────────────────────┘
                    │
                    │ contains
                    │
                    ▼
┌────────────────────────────────────────────────┐
│              DialogueLine                      │
├────────────────────────────────────────────────┤
│ + speaker: str                                 │
│ + text: str                                    │
│ + audio_file_path: str                         │
│ + start_time: float                            │
│ + duration: float                              │
└────────────────────────────────────────────────┘


┌────────────────────────────────────────────────┐
│             RawThreadData                      │
├────────────────────────────────────────────────┤
│ + title: str                                   │
│ + content: str                                 │
│ + author: str                                  │
│ + subreddit: str                               │
│ + upvotes: int                                 │
│ + comments: List[Dict]                         │
└────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────┐
│           Error Handling Strategy                │
└──────────────────────────────────────────────────┘

Generate Script Call
        │
        ▼
┌───────────────┐
│ Try Block     │
└───┬───────────┘
    │
    ├──► Build Prompt
    │    ├─ Success ──┐
    │    └─ Error ────┼──► Log Error ──► Fallback
    │                 │
    ├──► Call LLM     │
    │    ├─ Success ──┤
    │    ├─ HTTP Error┼──► Log Error ──► Fallback
    │    ├─ Timeout   │
    │    └─ Auth Error│
    │                 │
    ├──► Parse JSON   │
    │    ├─ Success ──┤
    │    ├─ JSONError ┼──► Log Error ──► Fallback
    │    └─ Format    │
    │                 │
    ├──► Validate     │
    │    ├─ Valid ────┼──► Return Script
    │    └─ Invalid ──┼──► Log Error ──► Fallback
    │                 │
    └──► Exception    │
         └────────────┼──► Log Error ──► Fallback
                      │
                      ▼
              ┌──────────────┐
              │ Fallback:    │
              │ Mock Script  │
              └──────────────┘
```

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TokSmith Ecosystem                        │
└─────────────────────────────────────────────────────────────┘

External Sources               Core Services           Output
┌──────────────┐              ┌──────────┐         ┌─────────┐
│   Reddit     │─────┐        │  Input   │         │  TTS    │
└──────────────┘     │        │ Service  │         └────┬────┘
                     │        └────┬─────┘              │
┌──────────────┐     │             │                    │
│   Twitter    │─────┼────────────►│                    │
└──────────────┘     │             │                    │
                     │             ▼                    │
┌──────────────┐     │        ┌──────────┐             │
│  StackOverf. │─────┘        │   LLM    │             │
└──────────────┘              │ Service  │             │
                              └────┬─────┘             │
┌──────────────┐                   │                   │
│   Podcast    │──────────────────►│                   │
└──────────────┘                   │                   │
                                   ▼                   │
┌──────────────┐              ┌──────────┐            │
│   Script     │─────────────►│  Script  │◄───────────┘
└──────────────┘              │  Entity  │
                              └────┬─────┘
                                   │
                                   ▼
                              ┌──────────┐
                              │  Video   │
                              │ Service  │
                              └────┬─────┘
                                   │
                                   ▼
                              ┌──────────┐
                              │ Storage  │
                              │ Service  │
                              └──────────┘
```

## File Structure Tree

```
Toksmith/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── script.py              ← Script & DialogueLine models
│   │
│   └── services/
│       └── llm_service/
│           ├── __init__.py         ← Package exports
│           ├── gemini_client.py    ← Gemini API wrapper
│           ├── llm_service.py      ← Main service logic
│           └── README.md           ← Detailed docs
│
├── examples/
│   └── llm_service_example.py     ← Working example
│
├── tests/
│   └── test_llm_service.py        ← Unit tests
│
├── scripts/
│   └── setup_llm_service.sh       ← Setup automation
│
├── .env.example                    ← Environment template
├── requirements.txt                ← Dependencies
├── LLM_MODULE.md                   ← Module overview
└── IMPLEMENTATION_SUMMARY.md       ← What was built
```

---

**Legend:**
- `►` Data flow
- `◄` Return flow
- `─` Connection
- `┐└├` Flow branches
- `▼` Downward flow
