"""
Authentication Schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Request Schemas
class UserSignUp(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


class UserSignIn(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordUpdate(BaseModel):
    """Password update request"""
    new_password: str = Field(..., min_length=8)


class EmailUpdate(BaseModel):
    """Email update request"""
    new_email: EmailStr


# Response Schemas
class UserResponse(BaseModel):
    """User data response"""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with tokens"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "uuid-here",
                    "email": "user@example.com",
                    "full_name": "John Doe"
                },
                "access_token": "eyJ...",
                "refresh_token": "eyJ...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True
