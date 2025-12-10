"""
API routes for Input Layer
"""
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from src.models import (
    ContentRequest,
    ContentResponse,
    ErrorResponse,
    InputSource,
    ScrapedContent,
    Status
)
from src.service import InputService
from src.url_validator import validate_url, infer_source_from_url
from src.database import SessionLocal, ScrapeJob
from src.tasks import process_scraped_content


router = APIRouter(prefix="/api/v1/input", tags=["Input Layer"])
input_service = InputService()


@router.post(
    "/scrape",
    response_model=ContentResponse,
    summary="Scrape content from various sources",
    description="Fetch and parse content from Reddit, Twitter, or StackOverflow"
)
async def scrape_content(request: ContentRequest):
    """
    Scrape content from supported sources
    
    - **Reddit**: Provide a Reddit thread URL
    - **Twitter**: Provide a Twitter/X thread URL
    - **StackOverflow**: Provide a StackOverflow question URL
    
    Returns job ID, content is processed asynchronously
    """
    db = SessionLocal()
    try:
        logger.info(f"Received scrape request for source: {request.source} and url: {request.url}")

        # If source omitted, try to infer from URL
        resolved_source = request.source
        if not resolved_source and request.url:
            inferred, infer_err = infer_source_from_url(str(request.url))
            if not inferred:
                raise HTTPException(status_code=400, detail=infer_err)
            resolved_source = inferred

        # Validate request for URL-based sources
        if resolved_source in [InputSource.REDDIT, InputSource.TWITTER, InputSource.STACKOVERFLOW]:
            if not request.url:
                raise HTTPException(
                    status_code=400,
                    detail=f"URL is required for {resolved_source} source"
                )

            # Validate URL explicitly for the resolved source
            is_valid, error_msg = validate_url(str(request.url), resolved_source)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)

            # Generate job ID
            job_id = str(uuid.uuid4())

            # Create job in database
            job = ScrapeJob(
                job_id=job_id,
                source=resolved_source.value,
                url=str(request.url),
                status=Status.PENDING
            )
            db.add(job)
            db.commit()

            # Queue job for processing (Celery)
            process_scraped_content.delay(job_id, resolved_source.value, str(request.url))

            return ContentResponse(
                success=True,
                message=f"Job queued successfully",
                job_id=job_id
            )

        elif resolved_source == InputSource.SCRIPT:
            if not request.script:
                raise HTTPException(
                    status_code=400,
                    detail="Script text is required for script source"
                )
            
            # Create content from script
            scraped_data = input_service.create_content_from_script(request.script)
            
            return ContentResponse(
                success=True,
                message="Script processed successfully",
                data=scraped_data
            )
        
        else:
            # If we get here, the source is either unsupported or missing and not inferable
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported or missing source. Provide a valid URL or set the 'source' field."
            )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        db.close()


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Check if the input layer service is running"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "input-layer",
        "version": "0.1.0"
    }


@router.get(
    "/sources",
    summary="List supported sources",
    description="Get list of supported input sources"
)
async def list_sources():
    """Get list of supported sources"""
    return {
        "sources": [
            {
                "name": "reddit",
                "description": "Reddit threads and discussions",
                "requires_url": True
            },
            {
                "name": "twitter",
                "description": "Twitter/X threads and conversations",
                "requires_url": True
            },
            {
                "name": "stackoverflow",
                "description": "StackOverflow questions and answers",
                "requires_url": True
            },
            {
                "name": "script",
                "description": "Direct script input",
                "requires_url": False,
                "requires_text": True
            },
            {
                "name": "podcast",
                "description": "Podcast audio files (coming soon)",
                "requires_url": False,
                "requires_file": True
            }
        ]
    }


@router.get(
    "/jobs/{job_id}",
    summary="Get job status",
    description="Get the status and result of a scraping job"
)
async def get_job_status(job_id: str):
    """Get job status and results"""
    db = SessionLocal()
    try:
        job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.job_id,
            "source": job.source,
            "url": job.url,
            "status": job.status.value,
            "data": job.scraped_data if job.status == Status.COMPLETED else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
    finally:
        db.close()

