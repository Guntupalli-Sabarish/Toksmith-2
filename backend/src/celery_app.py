"""
Celery configuration for job queue
"""
from celery import Celery
from src.config import settings

celery_app = Celery(
    "toksmith",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

