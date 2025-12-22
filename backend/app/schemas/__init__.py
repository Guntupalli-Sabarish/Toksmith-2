"""
Schemas module initialization
"""
from app.schemas.auth import (
    UserSignUp,
    UserSignIn,
    TokenRefresh,
    PasswordReset,
    PasswordUpdate,
    EmailUpdate,
    UserResponse,
    AuthResponse,
    MessageResponse
)
from app.schemas.user import (
    SubscriptionTier,
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileStats
)
from app.schemas.project import (
    ProjectStatus,
    SourceType,
    VideoStyle,
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ScrapedContent,
    ScriptData,
    ProjectResponse,
    ProjectListResponse
)
from app.schemas.storage import (
    FileType,
    FileUploadResponse,
    FileListResponse,
    SignedUrlRequest,
    SignedUrlResponse
)

__all__ = [
    # Auth
    "UserSignUp",
    "UserSignIn",
    "TokenRefresh",
    "PasswordReset",
    "PasswordUpdate",
    "EmailUpdate",
    "UserResponse",
    "AuthResponse",
    "MessageResponse",
    # User
    "SubscriptionTier",
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProfileStats",
    # Project
    "ProjectStatus",
    "SourceType",
    "VideoStyle",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ScrapedContent",
    "ScriptData",
    "ProjectResponse",
    "ProjectListResponse",
    # Storage
    "FileType",
    "FileUploadResponse",
    "FileListResponse",
    "SignedUrlRequest",
    "SignedUrlResponse"
]
