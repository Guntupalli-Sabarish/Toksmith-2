"""
Configuration management for the Input Layer
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Reddit API
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "toksmith-bot/1.0"
    
    # Twitter/X API
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    # LLM Service (for future integration)
    llm_service_url: str = "http://localhost:8001"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/toksmith_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"


# Global settings instance
settings = Settings()

