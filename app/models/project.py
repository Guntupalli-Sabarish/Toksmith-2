import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from app.db.base import Base

class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    SCRAPED = "scraped"
    SCRIPT_GENERATED = "script_generated"
    FAILED = "failed"

class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    scraped_data = Column(JSON, nullable=True)
    script_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
