"""
Storage Schemas for file uploads
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    AVATAR = "avatar"
    THUMBNAIL = "thumbnail"
    ASSET = "asset"


class FileUploadResponse(BaseModel):
    """Response for successful file upload"""
    file_id: str
    file_name: str
    file_path: str
    public_url: str
    file_type: FileType
    file_size: int
    mime_type: str
    created_at: datetime


class FileListResponse(BaseModel):
    """List of files response"""
    files: List[FileUploadResponse]
    total: int


class SignedUrlRequest(BaseModel):
    """Request for signed URL"""
    file_path: str
    expires_in: int = Field(default=3600, ge=60, le=604800)  # 1 minute to 7 days


class SignedUrlResponse(BaseModel):
    """Signed URL response"""
    signed_url: str
    expires_at: datetime
