"""
Authentication Dependencies for FastAPI
Provides dependency injection for protected routes
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.core.supabase import get_supabase
from app.schemas.auth import UserResponse


# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the current authenticated user"""
    
    def __init__(
        self,
        id: str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        role: str = "authenticated"
    ):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.avatar_url = avatar_url
        self.role = role


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        CurrentUser object with user data
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = credentials.credentials
        client = get_supabase()
        
        # Verify token with Supabase
        response = client.auth.get_user(token)
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = response.user
        user_meta = user.user_metadata or {}
        
        return CurrentUser(
            id=user.id,
            email=user.email,
            full_name=user_meta.get("full_name"),
            avatar_url=user_meta.get("avatar_url"),
            role=user.role or "authenticated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Optional dependency for routes that work with or without authentication
    
    Returns:
        CurrentUser if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def get_admin_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to ensure user has admin role
    
    Args:
        current_user: Authenticated user from get_current_user
        
    Returns:
        CurrentUser if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "service_role":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_subscription_tier(required_tier: str):
    """
    Factory function to create dependency for subscription tier check
    
    Args:
        required_tier: Minimum subscription tier required ('free', 'pro', 'enterprise')
        
    Returns:
        Dependency function
    """
    tier_levels = {"free": 0, "pro": 1, "enterprise": 2}
    required_level = tier_levels.get(required_tier, 0)
    
    async def check_subscription(
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        try:
            client = get_supabase()
            
            # Get user profile with subscription info
            response = client.table("profiles").select("subscription_tier").eq("id", current_user.id).maybe_single().execute()
            
            if response.data is None:
                # No profile yet - assume free tier
                user_tier = "free"
            else:
                user_tier = response.data.get("subscription_tier", "free")
            
            user_level = tier_levels.get(user_tier, 0)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires {required_tier} subscription or higher"
                )
            
            return current_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Subscription check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify subscription"
            )
    
    return check_subscription
