"""
Main API Router - Aggregates all API routes
"""
from fastapi import APIRouter

# Import v1 routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.projects_api import router as projects_router
from app.api.v1.storage import router as storage_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include all routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(projects_router)
router.include_router(storage_router)


# Health check endpoint
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "toksmith-api", "version": "1.0.0"}
