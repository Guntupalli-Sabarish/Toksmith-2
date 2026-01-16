import os
from pydantic import BaseConfig
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT Settings
    jwt_secret: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Storage Buckets
    storage_bucket_videos: str = os.getenv("STORAGE_BUCKET_VIDEOS", "videos")
    storage_bucket_audio: str = os.getenv("STORAGE_BUCKET_AUDIO", "audio")
    storage_bucket_avatars: str = os.getenv("STORAGE_BUCKET_AVATARS", "avatars")
    storage_bucket_assets: str = os.getenv("STORAGE_BUCKET_ASSETS", "assets")
    
    # Reddit
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "Toksmith/0.1")
    
    # Twitter
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_secret: str = os.getenv("TWITTER_ACCESS_SECRET", "")
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")

    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Hume AI (TTS)
    hume_api_key: str = os.getenv("HUME_API_KEY", "")

    # App Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Video Processing
    ffmpeg_path: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    ffprobe_path: str = os.getenv("FFPROBE_PATH", "ffprobe")
    local_storage_path: str = os.getenv("LOCAL_STORAGE_PATH", "static")

settings = Settings()
