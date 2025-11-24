"""
Data models and schemas for Input Layer
"""
from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class InputSource(str, Enum):
    """Supported input sources"""
    REDDIT = "reddit"
    TWITTER = "twitter"
    STACKOVERFLOW = "stackoverflow"
    SCRIPT = "script"
    PODCAST = "podcast"


class Status(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentRequest(BaseModel):
    """Request model for content input

    Notes:
    - `source` is optional. If not provided, the API will attempt to infer the
      source from the provided `url`.
    - For `script` source, provide `script` text.
    """
    source: Optional[InputSource] = Field(
        None, description="Optional: Source type of the content; if omitted the service will infer from the url"
    )
    url: Optional[HttpUrl] = Field(None, description="URL for Reddit, Twitter, or StackOverflow")
    script: Optional[str] = Field(None, description="Direct script text (max 10000 characters)")

    @model_validator(mode='after')
    def validate_input(self):
        """Ensure either URL or script is provided and basic consistency checks.

        We do not require `source` because the endpoint can infer it from the URL.
        """
        # If script source explicitly provided, script must be present
        if self.source == InputSource.SCRIPT:
            if not self.script:
                raise ValueError("Script text is required for script source")

        # If no source and no url and no script, reject
        if not self.source and not self.url and not self.script:
            raise ValueError("Either 'url' or 'script' must be provided")

        # If source is a URL-based source ensure url exists
        if self.source in [InputSource.REDDIT, InputSource.TWITTER, InputSource.STACKOVERFLOW] and not self.url:
            raise ValueError(f"URL is required for {self.source} source")

        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "reddit",
                "url": "https://www.reddit.com/r/programming/comments/example123"
            }
        }


class PostComment(BaseModel):
    """Model for individual comments/posts"""
    id: str
    author: Optional[str] = None
    content: str
    upvotes: int = 0
    timestamp: Optional[datetime] = None
    replies: List['PostComment'] = []


class ScrapedContent(BaseModel):
    """Model for scraped content from various sources"""
    source: InputSource
    url: Optional[str] = None
    title: str
    author: Optional[str] = None
    content: str
    comments: List[PostComment] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContentResponse(BaseModel):
    """Response model for content request"""
    success: bool
    message: str
    data: Optional[ScrapedContent] = None
    job_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

