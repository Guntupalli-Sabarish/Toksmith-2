# ToksMith — Input Layer (Mini-MVP)

This repository contains the Input Layer for ToksMith: a small FastAPI service that accepts a pasted URL or a script, infers the source (Reddit / Twitter(X) / StackOverflow), validates it, persists a short-lived job record, and enqueues a Celery task to scrape/process the content.

This project is intentionally minimal: it focuses on accepting URL input, routing requests to the appropriate scraper, storing temporary data in the database, and handing jobs off to Celery for further processing (LLM/TTS/video steps are out of scope here).

## What this does
- Accepts user input via POST /api/v1/input/scrape
- If `source` is omitted, infers source from the pasted URL (reddit/twitter/stackoverflow)
- Validates URL formats per source
- Persists a `scrape_jobs` DB record (temporary storage)
- Enqueues a Celery task (`process_scraped_content`) to run the scraper and store scraped JSON
- Provides endpoints to check supported sources and job status

## Project layout (important files)
- `src/main.py` — FastAPI application entry
- `src/api/routes.py` — input-layer API routes
- `src/service.py` — orchestrates scrapers
- `src/scrapers/*` — scrapers for reddit, twitter, stackoverflow
- `src/url_validator.py` — URL validation and inference
- `src/tasks.py` — Celery tasks that process queued jobs
- `src/celery_app.py` — Celery configuration
- `src/database.py` — SQLAlchemy model for `scrape_jobs`

## Quickstart (local, Windows / PowerShell)
Prerequisites:
- Python 3.10+ (project uses modern typing)
- Redis (or another broker supported by Celery) reachable by `REDIS_URL`
- A SQL database (Postgres recommended) reachable by `DATABASE_URL`

1. Install dependencies (create a virtualenv first if desired):

```powershell
cd 'e:/Toksmith Project'
python -m pip install -r requirements.txt
```

2. Configure environment variables (example):

```powershell
# $env:DATABASE_URL = 'postgresql://user:pass@localhost:5432/toksmith'
# $env:REDIS_URL = 'redis://localhost:6379/0'
# $env:API_HOST = '127.0.0.1'
# $env:API_PORT = '8000'
# Optional API credentials for scrapers (if you plan to use live APIs):
# $env:REDDIT_CLIENT_ID = '...'
# $env:REDDIT_CLIENT_SECRET = '...'
# $env:REDDIT_USER_AGENT = 'toksmith/0.1'
# $env:TWITTER_BEARER_TOKEN = '...'
```

3. Initialize DB (the app attempts to create tables on startup; you can also run `src.database.init_db()` manually).

4. Start the API server:

```powershell
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

5. Start a Celery worker in another shell:

```powershell
cd 'e:/Toksmith Project'
celery -A src.celery_app.celery_app worker --loglevel=info
```

## API (basic)
- POST /api/v1/input/scrape
  - Body: JSON with either `url` (HttpUrl) or `script` (string). `source` is optional.
  - If `source` omitted, the server will attempt to infer it from `url`.
  - Returns: { success, message, job_id }

- GET /api/v1/input/jobs/{job_id}
  - Returns job status and scraped data once completed.

- GET /api/v1/input/health
- GET /api/v1/input/sources

Example (PowerShell):

```powershell
# $body = @{ url = 'https://www.reddit.com/r/programming/comments/abcd1234/example' } | ConvertTo-Json
# Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/input/scrape' -Method Post -ContentType 'application/json' -Body $body
```

Example (curl):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/input/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.reddit.com/r/programming/comments/abcd1234/example"}'
```

## Configuration
The service reads configuration from `src/config.py` (environment variables). Key variables to set:
- `DATABASE_URL` — SQLAlchemy database URL
- `REDIS_URL` — Celery broker & backend
- `API_HOST`, `API_PORT` — server binding
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` — (optional) for Reddit API
- `TWITTER_BEARER_TOKEN` — (optional) for Twitter API

## Removing unwanted files
If you want a very small repo (docs, tests, and unused scrapers removed), you can delete files like `test_example.py`, `logs/`, and any scrapers you don't need under `src/scrapers/`. If you remove scrapers, update `src/service.py` and `src/models.py` to remove the corresponding `InputSource` entries — failing to do so will raise import errors. If you'd like, I can perform these deletions and the needed code changes for you.

## Development notes
- Scrapers are implemented as classes under `src/scrapers/` with an async `scrape(url)` method.
- `InputService.scrape_content` orchestrates the selection of the right scraper and calls its `scrape`.
- Celery task `process_scraped_content` updates job status in the database and stores scraped JSON.

## Tests
- There is an example test file `test_example.py`. Automated testing isn't required to run the service, but adding unit tests for the URL inference and API routes is recommended.

## Troubleshooting
- If Celery tasks don't run, verify `REDIS_URL` is correct and a worker is running.
- If scrapers fail with auth errors, set the relevant API credentials in environment variables or use the scraper in a read-only scraping mode if implemented.
- If `pytest` isn't installed and you want to run tests, install it with `pip install pytest`.

---

If you'd like, I can now remove the non-essential files (docs/tests/logs) or prune scrapers to keep only Reddit. Tell me which you'd like removed and I'll do it and report back.
