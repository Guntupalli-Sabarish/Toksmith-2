from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from app.models.input import ContentRequest, InputSource
from app.services.input_service.input_layer import InputService
from app.services.llm_service.llm_service import LLMService, RawThreadData
from app.core.config import settings
from app.db.session import get_db
from app.models.project import VideoProject, ProjectStatus

router = APIRouter()
input_service = InputService()
llm_service = LLMService(api_key=settings.gemini_api_key)

@router.post(
    "/projects/init",
    summary="Initialize Project (Scrape)",
    description="Initialize a video project by scraping content from a URL"
)
async def init_project(request: ContentRequest, db: Session = Depends(get_db)):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    try:
        logger.info(f"Initializing project for URL: {request.url}")
        
        # 1. Scrape Content
        scraped_content = await input_service.scrape_content(InputSource.REDDIT, str(request.url))
        
        # 2. Save to DB
        # Convert Pydantic model to dict and handle datetime serialization
        scraped_dict = scraped_content.dict()
        if scraped_dict.get("timestamp"):
            scraped_dict["timestamp"] = scraped_dict["timestamp"].isoformat()
            
        project = VideoProject(
            source_url=str(request.url),
            source_type=InputSource.REDDIT.value,
            status=ProjectStatus.SCRAPED,
            scraped_data=scraped_dict
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return {
            "success": True,
            "project_id": str(project.id),
            "status": project.status,
            "data": project.scraped_data
        }
        
    except Exception as e:
        logger.error(f"Project initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/projects/{project_id}/confirm",
    summary="Confirm & Generate Script",
    description="Confirm scraped content and generate script"
)
async def confirm_project(project_id: str, db: Session = Depends(get_db)):
    try:
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.status != ProjectStatus.SCRAPED:
             # Allow regenerating if already generated, but ideally should be in scraped state
             pass

        logger.info(f"Generating script for project: {project_id}")
        
        # Reconstruct ScrapedContent from stored JSON
        scraped_data = project.scraped_data
        
        # Convert to RawThreadData
        raw_thread = RawThreadData(
            title=scraped_data.get("title", ""),
            content=scraped_data.get("content", ""),
            author=scraped_data.get("author", "Anonymous"),
            subreddit=scraped_data.get("metadata", {}).get("subreddit", "reddit"),
            upvotes=scraped_data.get("metadata", {}).get("upvotes", 0),
            comments=[
                {
                    "author": c.get("author"),
                    "content": c.get("content"),
                    "upvotes": c.get("upvotes", 0)
                }
                for c in scraped_data.get("comments", [])
            ]
        )
        
        # Generate Script
        script = await llm_service.generate_structured_script(raw_thread)
        
        # Update Project
        project.script_data = {
            "background": script.background,
            "lines": [
                {
                    "speaker": line.speaker,
                    "text": line.text,
                    "audio_file_path": line.audio_file_path,
                    "start_time": line.start_time,
                    "duration": line.duration
                }
                for line in script.lines
            ]
        }
        project.status = ProjectStatus.SCRIPT_GENERATED
        db.commit()
        db.refresh(project)
        
        return {
            "success": True,
            "project_id": str(project.id),
            "status": project.status,
            "script": project.script_data
        }

    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/projects/{project_id}",
    summary="Get Project Status",
    description="Get the status and data of a project"
)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {
        "project_id": str(project.id),
        "source_url": project.source_url,
        "status": project.status,
        "scraped_data": project.scraped_data,
        "script_data": project.script_data,
        "created_at": project.created_at.isoformat()
    }

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "input-layer"}
