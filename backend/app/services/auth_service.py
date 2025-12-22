"""
Authentication Service using Supabase Auth
"""
from typing import Optional, Dict, Any
from loguru import logger
from supabase_auth.errors import AuthApiError

from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.auth import UserSignUp, UserSignIn, UserResponse, AuthResponse


class AuthService:
    """Service for handling authentication operations with Supabase"""
    
    def __init__(self):
        self.client = get_supabase()
        self.admin_client = get_supabase_admin()
    
    async def sign_up(self, user_data: UserSignUp) -> AuthResponse:
        """
        Register a new user with Supabase Auth
        
        Args:
            user_data: User registration data
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            AuthApiError: If registration fails
        """
        try:
            # Sign up with Supabase Auth
            response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if response.user is None:
                raise ValueError("Failed to create user")
            
            logger.info(f"User registered: {user_data.email}")
            
            # Create user profile in profiles table
            await self._create_user_profile(
                user_id=response.user.id,
                email=user_data.email,
                full_name=user_data.full_name
            )
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_data.full_name,
                    created_at=response.user.created_at
                ),
                access_token=response.session.access_token if response.session else "",
                refresh_token=response.session.refresh_token if response.session else "",
                expires_in=response.session.expires_in if response.session else 0
            )
            
        except AuthApiError as e:
            logger.error(f"Sign up failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            raise
    
    async def sign_in(self, credentials: UserSignIn) -> AuthResponse:
        """
        Authenticate user with email and password
        
        Args:
            credentials: User login credentials
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            AuthApiError: If authentication fails
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if response.user is None or response.session is None:
                raise ValueError("Invalid credentials")
            
            logger.info(f"User signed in: {credentials.email}")
            
            # Get user metadata
            user_meta = response.user.user_metadata or {}
            
            # Ensure profile exists (for users who signed up before profile creation was added)
            await self._ensure_profile_exists(
                user_id=response.user.id,
                email=response.user.email,
                full_name=user_meta.get("full_name")
            )
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_meta.get("full_name"),
                    avatar_url=user_meta.get("avatar_url"),
                    created_at=response.user.created_at
                ),
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600
            )
            
        except AuthApiError as e:
            logger.error(f"Sign in failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            raise
    
    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out user and invalidate tokens
        
        Args:
            access_token: User's access token
            
        Returns:
            True if sign out successful
        """
        try:
            self.client.auth.sign_out()
            logger.info("User signed out")
            return True
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            raise
    
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            AuthResponse with new tokens
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.user is None or response.session is None:
                raise ValueError("Invalid refresh token")
            
            user_meta = response.user.user_metadata or {}
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_meta.get("full_name"),
                    avatar_url=user_meta.get("avatar_url"),
                    created_at=response.user.created_at
                ),
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600
            )
            
        except AuthApiError as e:
            logger.error(f"Token refresh failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise
    
    async def reset_password(self, email: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            
        Returns:
            True if email sent successfully
        """
        try:
            self.client.auth.reset_password_email(email)
            logger.info(f"Password reset email sent to: {email}")
            return True
        except AuthApiError as e:
            logger.error(f"Password reset failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            raise
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """
        Update user's password
        
        Args:
            access_token: User's access token
            new_password: New password
            
        Returns:
            True if password updated successfully
        """
        try:
            self.client.auth.update_user({"password": new_password})
            logger.info("Password updated successfully")
            return True
        except AuthApiError as e:
            logger.error(f"Password update failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            raise
    
    async def get_user(self, access_token: str) -> Optional[UserResponse]:
        """
        Get current user from access token
        
        Args:
            access_token: User's access token
            
        Returns:
            UserResponse if token valid, None otherwise
        """
        try:
            response = self.client.auth.get_user(access_token)
            
            if response.user is None:
                return None
            
            user_meta = response.user.user_metadata or {}
            
            return UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_meta.get("full_name"),
                avatar_url=user_meta.get("avatar_url"),
                created_at=response.user.created_at
            )
            
        except AuthApiError:
            return None
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
    
    async def verify_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token and return user data
        
        Args:
            access_token: JWT access token
            
        Returns:
            User data dict if valid, None otherwise
        """
        try:
            response = self.client.auth.get_user(access_token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "role": response.user.role,
                    "metadata": response.user.user_metadata
                }
            return None
            
        except Exception:
            return None
    
    async def _create_user_profile(
        self, 
        user_id: str, 
        email: str, 
        full_name: Optional[str] = None
    ) -> None:
        """
        Create user profile in profiles table
        
        Args:
            user_id: Supabase auth user ID
            email: User's email
            full_name: User's full name
        """
        try:
            self.admin_client.table("profiles").insert({
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "subscription_tier": "free",
                "credits_remaining": 10  # Free tier credits
            }).execute()
            
            logger.info(f"User profile created for: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create user profile: {str(e)}")
            # Don't raise - auth user was created, profile creation is secondary
    
    async def _ensure_profile_exists(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> None:
        """
        Ensure user profile exists, create if missing
        
        Args:
            user_id: Supabase auth user ID
            email: User's email
            full_name: User's full name
        """
        try:
            # Check if profile exists
            response = self.admin_client.table("profiles").select("id").eq(
                "id", user_id
            ).maybe_single().execute()
            
            if response.data is None:
                # Profile doesn't exist, create it
                await self._create_user_profile(user_id, email, full_name)
                
        except Exception as e:
            logger.error(f"Failed to ensure profile exists: {str(e)}")
            # Don't raise - this is a safety check


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get AuthService singleton instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
