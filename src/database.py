"""
Database setup for storing scraped content temporarily
"""
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.config import settings
from src.models import Status

Base = declarative_base()


class ScrapeJob(Base):
    """Database model for scraped content jobs"""
    __tablename__ = "scrape_jobs"
    
    job_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    url = Column(String)
    status = Column(SQLEnum(Status), default=Status.PENDING)
    scraped_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database connection
from src.config import settings
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

