"""
Celery tasks for processing scraped content and sending to LLM
"""
import asyncio
from src.celery_app import celery_app
from src.database import SessionLocal, ScrapeJob
from src.service import InputService
from src.models import InputSource, Status
from loguru import logger


@celery_app.task
def process_scraped_content(job_id: str, source: str, url: str):
    """
    Process scraped content and send to LLM service
    
    Args:
        job_id: Unique job identifier
        source: Source type (reddit, twitter, etc.)
        url: URL to scrape
    """
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(ScrapeJob).filter(ScrapeJob.job_id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        job.status = Status.PROCESSING
        db.commit()
        
        # Scrape content (async)
        service = InputService()
        scraped_data = asyncio.run(service.scrape_content(InputSource(source), url))
        
        # Store in database
        job.scraped_data = scraped_data.model_dump()
        job.status = Status.COMPLETED
        db.commit()
        
        # TODO: Send to LLM service
        logger.info(f"Sending to LLM service for job {job_id}")
        # send_to_llm(job_id, scraped_data)
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        if 'job' in locals() and db:
            job.status = Status.FAILED
            db.commit()
    finally:
        db.close()


