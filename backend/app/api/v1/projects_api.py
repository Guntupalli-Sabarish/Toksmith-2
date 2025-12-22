"""
Projects API Routes
Handles video project CRUD and workflow operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional
from loguru import logger

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatus
)
from app.services.project_service import get_project_service, ProjectService
from app.services.user_service import get_user_service, UserService
from app.core.dependencies import get_current_user, CurrentUser


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Create a new video generation project"
)
async def create_project(
    project_data: ProjectCreate,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Create a new video generation project.
    
    - **source_url**: URL to scrape content from (Reddit, Twitter, StackOverflow)
    - **title**: Optional project title
    - **description**: Optional project description
    - **video_style**: Target video format (tiktok, youtube_short, etc.)
    """
    try:
        project = await project_service.create_project(current_user.id, project_data)
        return project
    except Exception as e:
        logger.error(f"Create project error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects",
    description="List all projects for the current user"
)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    List all projects with optional filtering and pagination.
    """
    try:
        result = await project_service.list_projects(
            user_id=current_user.id,
            status=status,
            page=page,
            per_page=per_page
        )
        return result
    except Exception as e:
        logger.error(f"List projects error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list projects"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project",
    description="Get a specific project by ID"
)
async def get_project(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get a project by ID"""
    project = await project_service.get_project(project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update a project's basic information"
)
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """Update a project"""
    try:
        project = await project_service.update_project(
            project_id=project_id,
            user_id=current_user.id,
            update_data=update_data
        )
        return project
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update project error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project and all associated files"
)
async def delete_project(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """Delete a project"""
    try:
        await project_service.delete_project(project_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Delete project error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )


@router.post(
    "/{project_id}/scrape",
    response_model=ProjectResponse,
    summary="Scrape content",
    description="Scrape content from the project's source URL"
)
async def scrape_content(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Scrape content from the source URL.
    
    This will:
    1. Fetch content from the source URL
    2. Parse and structure the content
    3. Update the project with scraped data
    """
    try:
        project = await project_service.scrape_content(project_id, current_user.id)
        return project
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Scrape content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scrape content"
        )


@router.post(
    "/{project_id}/generate-script",
    response_model=ProjectResponse,
    summary="Generate script",
    description="Generate a video script from scraped content"
)
async def generate_script(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Generate a script from the scraped content.
    
    This will:
    1. Use AI to generate a structured video script
    2. Create dialogue lines with emotions
    3. Estimate video duration
    
    Requires credits (1 credit per script generation).
    """
    try:
        # Check credits
        profile = await user_service.get_profile(current_user.id)
        if not profile or profile.credits_remaining < 1:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits. Please purchase more credits."
            )
        
        # Generate script
        project = await project_service.generate_script(project_id, current_user.id)
        
        # Deduct credit
        await user_service.deduct_credits(
            user_id=current_user.id,
            amount=1,
            project_id=project_id,
            description="Script generation"
        )
        
        return project
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Generate script error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate script"
        )


@router.post(
    "/{project_id}/generate",
    response_model=ProjectResponse,
    summary="Full generation pipeline",
    description="Run the full video generation pipeline (scrape + script)"
)
async def generate_full(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Run the full video generation pipeline.
    
    This will:
    1. Scrape content from the source URL
    2. Generate a video script
    
    Requires credits (1 credit).
    """
    try:
        # Check credits
        profile = await user_service.get_profile(current_user.id)
        if not profile or profile.credits_remaining < 1:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits. Please purchase more credits."
            )
        
        # Scrape content
        project = await project_service.scrape_content(project_id, current_user.id)
        
        # Generate script
        project = await project_service.generate_script(project_id, current_user.id)
        
        # Deduct credit
        await user_service.deduct_credits(
            user_id=current_user.id,
            amount=1,
            project_id=project_id,
            description="Full pipeline generation"
        )
        
        return project
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Full generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run generation pipeline"
        )
