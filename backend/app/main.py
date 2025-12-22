"""
Main FastAPI application for TokSmith - AI Video Generation Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.api.route import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Starting TokSmith API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    
    # Initialize Supabase connection
    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Supabase initialization failed: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TokSmith API...")


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/input_layer.log",
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)


# Create FastAPI app
app = FastAPI(
    title="TokSmith API",
    description="""
    AI-Powered Video Generation Platform API
    
    ## Features
    - **Authentication**: User signup, login, and token management with Supabase Auth
    - **Projects**: Create and manage video generation projects
    - **Content Scraping**: Scrape content from Reddit, Twitter, StackOverflow
    - **Script Generation**: AI-powered script generation using Gemini
    - **Storage**: File upload and management with Supabase Storage
    - **Credits**: Usage-based credit system
    
    ## Authentication
    All endpoints (except /auth/*) require a valid JWT token in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TokSmith API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.environment == "development")
    )

