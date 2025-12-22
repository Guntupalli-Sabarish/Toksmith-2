"""
User Profile Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProfileBase(BaseModel):
    """Base profile schema"""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class ProfileCreate(ProfileBase):
    """Schema for creating a profile"""
    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile"""
    pass


class ProfileResponse(ProfileBase):
    """Profile response schema"""
    id: str
    email: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    credits_remaining: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProfileStats(BaseModel):
    """User statistics"""
    total_projects: int = 0
    total_videos_generated: int = 0
    credits_used: int = 0
    credits_remaining: int = 0
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
