"""
Authentication API Routes
Handles user authentication, registration, and token management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from loguru import logger
from supabase_auth.errors import AuthApiError

from app.schemas.auth import (
    UserSignUp,
    UserSignIn,
    TokenRefresh,
    PasswordReset,
    PasswordUpdate,
    AuthResponse,
    UserResponse,
    MessageResponse
)
from app.services.auth_service import get_auth_service, AuthService
from app.core.dependencies import get_current_user, CurrentUser


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def signup(
    user_data: UserSignUp,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user with email and password.
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    
    Returns authentication tokens and user data.
    """
    try:
        result = await auth_service.sign_up(user_data)
        return result
    except AuthApiError as e:
        logger.error(f"Signup failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate with email and password"
)
async def login(
    credentials: UserSignIn,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with email and password.
    
    Returns authentication tokens and user data.
    """
    try:
        result = await auth_service.sign_in(credentials)
        return result
    except AuthApiError as e:
        logger.error(f"Login failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Sign out and invalidate tokens"
)
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Sign out the current user and invalidate their session.
    
    Requires valid access token in Authorization header.
    """
    try:
        await auth_service.sign_out("")
        return MessageResponse(message="Successfully logged out")
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    token_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh the access token using a valid refresh token.
    
    Returns new authentication tokens.
    """
    try:
        result = await auth_service.refresh_token(token_data.refresh_token)
        return result
    except AuthApiError as e:
        logger.error(f"Token refresh failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post(
    "/password-reset",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email"
)
async def request_password_reset(
    data: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request a password reset email.
    
    - **email**: Email address of the account
    
    An email will be sent with a password reset link if the account exists.
    """
    try:
        await auth_service.reset_password(data.email)
        return MessageResponse(
            message="If an account exists with this email, a password reset link has been sent"
        )
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        # Don't reveal if email exists or not
        return MessageResponse(
            message="If an account exists with this email, a password reset link has been sent"
        )


@router.post(
    "/password-update",
    response_model=MessageResponse,
    summary="Update password",
    description="Update user's password (requires authentication)"
)
async def update_password(
    data: PasswordUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update the current user's password.
    
    - **new_password**: New password (minimum 8 characters)
    
    Requires valid access token.
    """
    try:
        await auth_service.update_password("", data.new_password)
        return MessageResponse(message="Password updated successfully")
    except AuthApiError as e:
        logger.error(f"Password update failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the current authenticated user's information"
)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get the current authenticated user's information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url
    )
