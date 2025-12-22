# TokSmith — AI Video Generation Platform Backend

A FastAPI-based backend for AI-powered video generation from social media content (Reddit, Twitter, StackOverflow). Built with Supabase for authentication, database, and file storage.

## Features

- **🔐 Authentication**: Secure user authentication with Supabase Auth
- **📂 Project Management**: Create, manage, and track video generation projects
- **🔍 Content Scraping**: Scrape content from Reddit, Twitter, StackOverflow
- **✍️ AI Script Generation**: Generate video scripts using Google Gemini AI
- **📦 File Storage**: Upload and manage files with Supabase Storage
- **💳 Credit System**: Usage-based credit system for video generation
- **🎬 Video Styles**: Support for TikTok, YouTube Shorts, Instagram Reels

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage
- **AI**: Google Gemini
- **Task Queue**: Celery + Redis

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Supabase account and project
- Redis (for Celery)
- Google AI API key (for Gemini)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Database
DATABASE_URL="postgresql://postgres:password@db.your-project.supabase.co:5432/postgres"

# JWT Settings
JWT_SECRET="your-jwt-secret-key-change-in-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage Buckets
STORAGE_BUCKET_VIDEOS="videos"
STORAGE_BUCKET_AUDIO="audio"
STORAGE_BUCKET_AVATARS="avatars"
STORAGE_BUCKET_ASSETS="assets"

# Google Gemini AI
GEMINI_API_KEY="your-gemini-api-key"

# Reddit API (for scraping)
REDDIT_CLIENT_ID="your-reddit-client-id"
REDDIT_CLIENT_SECRET="your-reddit-client-secret"
REDDIT_USER_AGENT="TokSmith/1.0"

# App Settings
ENVIRONMENT="development"
LOG_LEVEL="INFO"
API_HOST="0.0.0.0"
API_PORT=8000
```

### 4. Supabase Setup

#### Database Tables

Run the SQL migration in your Supabase SQL Editor:

```bash
# Run the migration file
cat supabase/migrations/001_initial_schema.sql
```

This creates:
- `profiles` - User profiles extending Supabase Auth
- `projects` - Video generation projects
- `video_jobs` - Async processing jobs
- `generated_files` - File records
- `credit_transactions` - Credit history

#### Storage Buckets

1. Go to Supabase Dashboard → Storage
2. Create the following buckets:
   - `videos` - For generated videos
   - `audio` - For generated audio
   - `avatars` - For user profile pictures (public)
   - `assets` - For misc assets

3. Run storage policies from `supabase/migrations/002_storage_policies.sql`

### 5. Run the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
python run_server.py
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/login` | User login |
| POST | `/logout` | User logout |
| POST | `/refresh` | Refresh access token |
| POST | `/password-reset` | Request password reset |
| POST | `/password-update` | Update password |
| GET | `/me` | Get current user |

### Users (`/api/v1/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me/profile` | Get user profile |
| PATCH | `/me/profile` | Update profile |
| POST | `/me/avatar` | Upload avatar |
| GET | `/me/stats` | Get user statistics |
| GET | `/me/credits` | Get credit balance |

### Projects (`/api/v1/projects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create new project |
| GET | `/` | List projects |
| GET | `/{id}` | Get project |
| PATCH | `/{id}` | Update project |
| DELETE | `/{id}` | Delete project |
| POST | `/{id}/scrape` | Scrape content |
| POST | `/{id}/generate-script` | Generate script |
| POST | `/{id}/generate` | Full pipeline |

### Storage (`/api/v1/storage`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload file |
| GET | `/files` | List files |
| GET | `/files/{id}/download` | Download file |
| POST | `/files/{id}/signed-url` | Get signed URL |
| DELETE | `/files/{id}` | Delete file |

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── users.py         # User endpoints
│   │   │   ├── projects_api.py  # Project endpoints
│   │   │   └── storage.py       # Storage endpoints
│   │   └── route.py             # Main router
│   ├── core/
│   │   ├── config.py            # App configuration
│   │   ├── supabase.py          # Supabase client
│   │   └── dependencies.py      # Auth dependencies
│   ├── schemas/
│   │   ├── auth.py              # Auth schemas
│   │   ├── user.py              # User schemas
│   │   ├── project.py           # Project schemas
│   │   └── storage.py           # Storage schemas
│   ├── services/
│   │   ├── auth_service.py      # Auth service
│   │   ├── user_service.py      # User service
│   │   ├── project_service.py   # Project service
│   │   ├── storage_service/     # Storage service
│   │   ├── input_service/       # Content scraping
│   │   └── llm_service/         # AI script generation
│   └── main.py                  # FastAPI app
├── supabase/
│   └── migrations/              # SQL migrations
├── requirements.txt
└── .env
```

## Authentication Flow

1. **Sign Up**: POST `/api/v1/auth/signup`
   - Creates Supabase Auth user
   - Creates profile in `profiles` table
   - Returns access and refresh tokens

2. **Sign In**: POST `/api/v1/auth/login`
   - Authenticates with Supabase Auth
   - Returns access and refresh tokens

3. **Protected Routes**: Include token in header
   ```
   Authorization: Bearer <access_token>
   ```

4. **Token Refresh**: POST `/api/v1/auth/refresh`
   - Exchange refresh token for new access token

## Credit System

- New users receive **10 free credits**
- Video generation costs **1 credit**
- Credits can be purchased (payment integration coming soon)

## Video Generation Pipeline

1. **Create Project**: Provide source URL
2. **Scrape Content**: Extract content from URL
3. **Generate Script**: AI creates video script
4. **Generate Audio**: TTS converts script to audio (coming soon)
5. **Generate Video**: Combine audio with visuals (coming soon)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## Deployment

### Docker

```bash
docker build -t toksmith-backend .
docker run -p 8000:8000 --env-file .env toksmith-backend
```

### Docker Compose

```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
