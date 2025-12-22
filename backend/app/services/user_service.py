"""
User Profile Service
Handles user profile management operations
"""
from typing import Optional
from loguru import logger

from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.user import ProfileResponse, ProfileUpdate, ProfileStats


class UserService:
    """Service for handling user profile operations"""
    
    def __init__(self):
        self.client = get_supabase()
        self.admin_client = get_supabase_admin()
    
    async def get_profile(self, user_id: str) -> Optional[ProfileResponse]:
        """
        Get user profile by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            ProfileResponse if found, None otherwise
        """
        try:
            response = self.admin_client.table("profiles").select("*").eq(
                "id", user_id
            ).maybe_single().execute()
            
            if not response.data:
                return None
            
            data = response.data
            return ProfileResponse(
                id=data["id"],
                email=data["email"],
                full_name=data.get("full_name"),
                avatar_url=data.get("avatar_url"),
                bio=data.get("bio"),
                subscription_tier=data.get("subscription_tier", "free"),
                credits_remaining=data.get("credits_remaining", 0),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at")
            )
            
        except Exception as e:
            logger.error(f"Failed to get profile: {str(e)}")
            return None
    
    async def update_profile(
        self, 
        user_id: str, 
        profile_data: ProfileUpdate
    ) -> ProfileResponse:
        """
        Update user profile
        
        Args:
            user_id: User's ID
            profile_data: Profile update data
            
        Returns:
            Updated ProfileResponse
            
        Raises:
            ValueError: If profile not found
        """
        try:
            # Build update dict, excluding None values
            update_dict = {
                k: v for k, v in profile_data.model_dump().items() 
                if v is not None
            }
            
            if not update_dict:
                # Nothing to update, return current profile
                return await self.get_profile(user_id)
            
            response = self.admin_client.table("profiles").update(
                update_dict
            ).eq("id", user_id).execute()
            
            if not response.data:
                raise ValueError("Profile not found")
            
            data = response.data[0]
            logger.info(f"Profile updated for user: {user_id}")
            
            return ProfileResponse(
                id=data["id"],
                email=data["email"],
                full_name=data.get("full_name"),
                avatar_url=data.get("avatar_url"),
                bio=data.get("bio"),
                subscription_tier=data.get("subscription_tier", "free"),
                credits_remaining=data.get("credits_remaining", 0),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at")
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update profile: {str(e)}")
            raise Exception(f"Failed to update profile: {str(e)}")
    
    async def update_avatar(self, user_id: str, avatar_url: str) -> ProfileResponse:
        """
        Update user's avatar URL
        
        Args:
            user_id: User's ID
            avatar_url: New avatar URL
            
        Returns:
            Updated ProfileResponse
        """
        try:
            response = self.admin_client.table("profiles").update({
                "avatar_url": avatar_url
            }).eq("id", user_id).execute()
            
            if not response.data:
                raise ValueError("Profile not found")
            
            # Also update auth metadata
            self.admin_client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": {"avatar_url": avatar_url}}
            )
            
            return await self.get_profile(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update avatar: {str(e)}")
            raise Exception(f"Failed to update avatar: {str(e)}")
    
    async def get_user_stats(self, user_id: str) -> ProfileStats:
        """
        Get user statistics
        
        Args:
            user_id: User's ID
            
        Returns:
            ProfileStats with user statistics
        """
        try:
            # Get profile - use maybe_single to handle missing profile gracefully
            profile_response = self.admin_client.table("profiles").select(
                "subscription_tier, credits_remaining"
            ).eq("id", user_id).maybe_single().execute()
            
            profile = profile_response.data or {}
            
            # Count projects
            projects_response = self.admin_client.table("projects").select(
                "id", count="exact"
            ).eq("user_id", user_id).execute()
            
            # Count completed videos
            videos_response = self.admin_client.table("projects").select(
                "id", count="exact"
            ).eq("user_id", user_id).eq("status", "completed").execute()
            
            # Calculate credits used - handle missing table gracefully
            credits_used = 0
            try:
                credits_response = self.admin_client.table("credit_transactions").select(
                    "amount"
                ).eq("user_id", user_id).eq("transaction_type", "usage").execute()
                credits_used = sum(abs(t["amount"]) for t in (credits_response.data or []))
            except Exception:
                # Table might not exist or be empty - that's okay
                pass
            
            return ProfileStats(
                total_projects=projects_response.count or 0,
                total_videos_generated=videos_response.count or 0,
                credits_used=credits_used,
                credits_remaining=profile.get("credits_remaining", 0),
                subscription_tier=profile.get("subscription_tier", "free")
            )
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            # Return default stats instead of raising an error
            return ProfileStats(
                total_projects=0,
                total_videos_generated=0,
                credits_used=0,
                credits_remaining=0,
                subscription_tier="free"
            )
    
    async def deduct_credits(
        self, 
        user_id: str, 
        amount: int, 
        project_id: Optional[str] = None,
        description: str = "Video generation"
    ) -> int:
        """
        Deduct credits from user's balance
        
        Args:
            user_id: User's ID
            amount: Number of credits to deduct
            project_id: Optional project ID
            description: Transaction description
            
        Returns:
            New balance
            
        Raises:
            ValueError: If insufficient credits
        """
        try:
            # Get current balance
            profile = await self.get_profile(user_id)
            if not profile:
                raise ValueError("Profile not found")
            
            if profile.credits_remaining < amount:
                raise ValueError("Insufficient credits")
            
            new_balance = profile.credits_remaining - amount
            
            # Update balance
            self.admin_client.table("profiles").update({
                "credits_remaining": new_balance
            }).eq("id", user_id).execute()
            
            # Record transaction
            self.admin_client.table("credit_transactions").insert({
                "user_id": user_id,
                "project_id": project_id,
                "amount": -amount,
                "transaction_type": "usage",
                "description": description,
                "balance_after": new_balance
            }).execute()
            
            logger.info(f"Deducted {amount} credits from user {user_id}. New balance: {new_balance}")
            return new_balance
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to deduct credits: {str(e)}")
            raise Exception(f"Failed to deduct credits: {str(e)}")
    
    async def add_credits(
        self, 
        user_id: str, 
        amount: int,
        transaction_type: str = "purchase",
        description: str = "Credits added"
    ) -> int:
        """
        Add credits to user's balance
        
        Args:
            user_id: User's ID
            amount: Number of credits to add
            transaction_type: Type of transaction (purchase, bonus, refund)
            description: Transaction description
            
        Returns:
            New balance
        """
        try:
            # Get current balance
            profile = await self.get_profile(user_id)
            if not profile:
                raise ValueError("Profile not found")
            
            new_balance = profile.credits_remaining + amount
            
            # Update balance
            self.admin_client.table("profiles").update({
                "credits_remaining": new_balance
            }).eq("id", user_id).execute()
            
            # Record transaction
            self.admin_client.table("credit_transactions").insert({
                "user_id": user_id,
                "amount": amount,
                "transaction_type": transaction_type,
                "description": description,
                "balance_after": new_balance
            }).execute()
            
            logger.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
            return new_balance
            
        except Exception as e:
            logger.error(f"Failed to add credits: {str(e)}")
            raise Exception(f"Failed to add credits: {str(e)}")


# Singleton instance
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get UserService singleton instance"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
