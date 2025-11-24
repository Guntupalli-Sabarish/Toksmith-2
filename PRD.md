**Project Name:** ToksMith

**Version:** v1.0

**Last Updated:** [Insert Date]

---

## 1. **Overview**

ToksMith is a platform that enables users to transform online content (Reddit threads, Twitter threads, StackOverflow Q&As, scripts, and podcasts) into short-form videos (reels/shorts). It automates the entire workflow — content ingestion, script generation, text-to-speech (TTS), video assembly, captions, and export.

The goal is to make content repurposing fast, engaging, and highly customizable.

---

## 2. **Objectives**

- Allow users to create professional-quality short videos in minutes.
- Support multiple input sources: Reddit, Twitter, StackOverflow, scripts, and podcasts.
- Provide automated pipelines for script creation, narration, captions, and video editing.
- Enable scalability with concurrency and background workers.
- Support customization: voices, templates, styles, background music.

---

## 3. **Key Features**

### **MVP Features (v1.0)**

1. **Content Input**
    - Paste Reddit/Twitter/StackOverflow thread URL.
    - Upload a podcast audio file.
    - Paste or upload custom script.
2. **Script Generation**
    - Summarize and adapt input into a short, engaging script.
    - Option for tone/style selection (educational, casual, professional, fun).
3. **Text-to-Speech (TTS)**
    - Self-hosted TTS engine for narration.
    - Multiple voice styles.
4. **Video Assembly**
    - Predefined templates (backgrounds, transitions).
    - Auto-caption generation.
    - Background music.
5. **Export & Storage**
    - Save final video to S3 (or equivalent).
    - Download link shared via frontend.
6. **Project Management**
    - User can create/manage multiple projects.
    - Each project has history of videos generated.

---

### **Future Enhancements (v2.0+)**

- AI voice cloning.
- Multi-language TTS and subtitles.
- Podcast auto-segmentation into highlights.
- Auto brand kit (logos, fonts, color palettes).
- Interactive editing: trim/replace audio/video.
- Real-time collaboration (like Figma for shorts).

---

## 4. **User Stories**

1. *As a user*, I want to paste a Reddit thread URL so that I can generate a short video summarizing the discussion.
2. *As a user*, I want to upload my podcast and get a 60-second highlight reel automatically.
3. *As a user*, I want to choose between different voices for narration.
4. *As a user*, I want to preview captions before finalizing the video.
5. *As a user*, I want to manage multiple projects and keep generated videos organized.

---

## 5. **System Architecture (High-Level)**

- **Frontend (Next.js)**: Input UI, project dashboard, video previews.
- **Backend (FastAPI)**: API handling requests, job queue management.
- **Processing Queues (Celery/Redis)**: Manages long-running tasks (LLM, TTS, Video Merge).
- **LLM Service**: Generates scripts, summaries.
- **TTS Service**: Converts text to narration.
- **Video Service**: Merges narration, captions, visuals, music.
- **Storage (S3/MinIO)**: Stores final videos.
- **Database (Postgres)**: Tracks users, projects, and videos.

---

## 6. **Dependencies**

- OpenAI / Local LLM for script generation.
- Self-hosted TTS (e.g., Coqui, Piper).
- FFMPEG for video processing.
- Redis/Celery for concurrency.
- MongoDB/Postgres for project management.

---

## 7. **KPIs / Success Metrics**

- Average time to generate a short video.
- User retention (projects created per user per month).
- Export/download completion rate.
- Processing failure rate < 5%.

---

## 8. **Risks & Mitigation**

- **Risk:** TTS quality might sound robotic → **Mitigation:** fine-tune self-hosted models, offer premium voices.
- **Risk:** Video generation latency. → **Mitigation:** concurrency with Celery + Redis, horizontal scaling of workers.
- **Risk:** Copyright concerns on input content → **Mitigation:** disclaimers + fair use guidelines.

---

## 9. **Roadmap (High-Level)**

**Q4 2025 (MVP):**

- Reddit/Twitter/Script to short video.
- Basic TTS + caption + template.
- Project management dashboard.

**Q1 2026:**

- Podcast to short video.
- More templates and voice styles.
- Export optimization.

**Q2 2026:**

- Multi-language + AI voice cloning.
- Collaborative editing.
- Brand kits.

---

⚡ That’s the **PRD v1.0 draft** — simple, structured, and covers everything.

Do you want me to also create a **matching LLD template** (Low-Level Design) so it pairs well with this PRD in Notion?