"""
Project Schemas for video generation projects
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    SCRAPED = "scraped"
    SCRIPT_GENERATED = "script_generated"
    AUDIO_GENERATED = "audio_generated"
    VIDEO_GENERATED = "video_generated"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceType(str, Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    STACKOVERFLOW = "stackoverflow"
    CUSTOM = "custom"


class VideoStyle(str, Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORT = "youtube_short"
    INSTAGRAM_REEL = "instagram_reel"
    YOUTUBE = "youtube"


class ProjectBase(BaseModel):
    """Base project schema"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    source_url: Optional[str] = None
    source_type: Optional[SourceType] = None
    video_style: VideoStyle = VideoStyle.TIKTOK


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    source_url: str = Field(..., description="URL to scrape content from")


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    video_style: Optional[VideoStyle] = None


class ScrapedContent(BaseModel):
    """Scraped content data"""
    title: str
    content: str
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    comments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ScriptData(BaseModel):
    """Generated script data"""
    script_text: str
    dialogue_lines: List[Dict[str, Any]] = []
    duration_estimate: Optional[float] = None
    word_count: int = 0


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: str
    user_id: str
    status: ProjectStatus = ProjectStatus.DRAFT
    scraped_data: Optional[Dict[str, Any]] = None
    script_data: Optional[Dict[str, Any]] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List of projects response"""
    projects: List[ProjectResponse]
    total: int
    page: int = 1
    per_page: int = 20
