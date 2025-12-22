"""
User Profile API Routes
Handles user profile management
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from loguru import logger

from app.schemas.user import ProfileResponse, ProfileUpdate, ProfileStats
from app.services.user_service import get_user_service, UserService
from app.services.storage_service.storage import get_storage_service, StorageService
from app.schemas.storage import FileType
from app.core.dependencies import get_current_user, CurrentUser


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me/profile",
    response_model=ProfileResponse,
    summary="Get current user's profile",
    description="Get the authenticated user's full profile information"
)
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's profile"""
    profile = await user_service.get_profile(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.patch(
    "/me/profile",
    response_model=ProfileResponse,
    summary="Update profile",
    description="Update the current user's profile information"
)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update the current user's profile"""
    try:
        profile = await user_service.update_profile(current_user.id, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post(
    "/me/avatar",
    response_model=ProfileResponse,
    summary="Upload avatar",
    description="Upload a new profile picture"
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Upload a new avatar image"""
    try:
        # Read file
        file_data = await file.read()
        
        # Upload to storage
        upload_result = await storage_service.upload_file(
            user_id=current_user.id,
            file_data=file_data,
            file_name=file.filename or "avatar",
            file_type=FileType.AVATAR,
            mime_type=file.content_type or "image/jpeg",
            make_public=True
        )
        
        # Update profile with new avatar URL
        profile = await user_service.update_avatar(current_user.id, upload_result.public_url)
        return profile
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Avatar upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar"
        )


@router.get(
    "/me/stats",
    response_model=ProfileStats,
    summary="Get user statistics",
    description="Get the current user's usage statistics"
)
async def get_my_stats(
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's statistics"""
    try:
        stats = await user_service.get_user_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error(f"Stats retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.get(
    "/me/credits",
    summary="Get credit balance",
    description="Get the current user's credit balance"
)
async def get_credit_balance(
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's credit balance"""
    profile = await user_service.get_profile(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return {
        "credits_remaining": profile.credits_remaining,
        "subscription_tier": profile.subscription_tier
    }
