"""
Storage Service using Supabase Storage
Handles file uploads, downloads, and management for videos, audio, avatars, etc.
"""
import uuid
from typing import Optional, List, BinaryIO
from datetime import datetime, timedelta
from loguru import logger

from app.core.supabase import get_supabase, get_supabase_admin
from app.core.config import settings
from app.schemas.storage import FileType, FileUploadResponse, FileListResponse, SignedUrlResponse


class StorageService:
    """Service for handling file storage operations with Supabase Storage"""
    
    # Bucket configuration
    BUCKET_MAPPING = {
        FileType.VIDEO: "videos",
        FileType.AUDIO: "audio",
        FileType.AVATAR: "avatars",
        FileType.IMAGE: "assets",
        FileType.THUMBNAIL: "assets",
        FileType.ASSET: "assets"
    }
    
    # Allowed MIME types per file type
    ALLOWED_MIME_TYPES = {
        FileType.VIDEO: ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"],
        FileType.AUDIO: ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3", "audio/x-wav"],
        FileType.IMAGE: ["image/jpeg", "image/png", "image/gif", "image/webp"],
        FileType.AVATAR: ["image/jpeg", "image/png", "image/webp"],
        FileType.THUMBNAIL: ["image/jpeg", "image/png", "image/webp"],
        FileType.ASSET: ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"]
    }
    
    # Max file sizes in bytes
    MAX_FILE_SIZES = {
        FileType.VIDEO: 500 * 1024 * 1024,  # 500 MB
        FileType.AUDIO: 50 * 1024 * 1024,   # 50 MB
        FileType.IMAGE: 10 * 1024 * 1024,   # 10 MB
        FileType.AVATAR: 5 * 1024 * 1024,   # 5 MB
        FileType.THUMBNAIL: 5 * 1024 * 1024, # 5 MB
        FileType.ASSET: 20 * 1024 * 1024    # 20 MB
    }
    
    def __init__(self):
        self.client = get_supabase()
        self.admin_client = get_supabase_admin()
    
    def _get_bucket_name(self, file_type: FileType) -> str:
        """Get the bucket name for a file type"""
        return self.BUCKET_MAPPING.get(file_type, "assets")
    
    def _generate_file_path(
        self, 
        user_id: str, 
        file_type: FileType, 
        original_filename: str,
        project_id: Optional[str] = None
    ) -> str:
        """
        Generate a unique file path for storage
        
        Format: user_id/[project_id/]file_type/uuid_filename
        """
        # Generate unique filename
        file_extension = original_filename.split(".")[-1] if "." in original_filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        # Build path
        if project_id:
            return f"{user_id}/{project_id}/{file_type.value}/{unique_filename}"
        return f"{user_id}/{file_type.value}/{unique_filename}"
    
    def _validate_file(
        self, 
        file_type: FileType, 
        mime_type: str, 
        file_size: int
    ) -> None:
        """
        Validate file type and size
        
        Raises:
            ValueError: If validation fails
        """
        allowed_types = self.ALLOWED_MIME_TYPES.get(file_type, [])
        if mime_type not in allowed_types:
            raise ValueError(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        max_size = self.MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024)
        if file_size > max_size:
            raise ValueError(f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB")
    
    async def upload_file(
        self,
        user_id: str,
        file_data: bytes,
        file_name: str,
        file_type: FileType,
        mime_type: str,
        project_id: Optional[str] = None,
        make_public: bool = False
    ) -> FileUploadResponse:
        """
        Upload a file to Supabase Storage
        
        Args:
            user_id: Owner's user ID
            file_data: File content as bytes
            file_name: Original filename
            file_type: Type of file (video, audio, etc.)
            mime_type: MIME type of the file
            project_id: Optional project ID to associate with
            make_public: Whether to generate a public URL
            
        Returns:
            FileUploadResponse with file details
            
        Raises:
            ValueError: If validation fails
            Exception: If upload fails
        """
        try:
            # Validate file
            self._validate_file(file_type, mime_type, len(file_data))
            
            # Get bucket and generate path
            bucket_name = self._get_bucket_name(file_type)
            file_path = self._generate_file_path(user_id, file_type, file_name, project_id)
            
            logger.info(f"Uploading file to {bucket_name}/{file_path}")
            
            # Upload to Supabase Storage
            storage = self.admin_client.storage.from_(bucket_name)
            response = storage.upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": mime_type}
            )
            
            # Generate public URL if requested
            public_url = ""
            if make_public:
                public_url = storage.get_public_url(file_path)
            
            # Record in database
            file_id = str(uuid.uuid4())
            self.admin_client.table("generated_files").insert({
                "id": file_id,
                "user_id": user_id,
                "project_id": project_id,
                "file_name": file_name,
                "file_path": file_path,
                "file_type": file_type.value,
                "file_size": len(file_data),
                "mime_type": mime_type,
                "bucket_name": bucket_name,
                "public_url": public_url if make_public else None,
                "is_public": make_public
            }).execute()
            
            logger.info(f"File uploaded successfully: {file_id}")
            
            return FileUploadResponse(
                file_id=file_id,
                file_name=file_name,
                file_path=file_path,
                public_url=public_url,
                file_type=file_type,
                file_size=len(file_data),
                mime_type=mime_type,
                created_at=datetime.utcnow()
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def get_signed_url(
        self,
        user_id: str,
        file_path: str,
        bucket_name: str,
        expires_in: int = 3600
    ) -> SignedUrlResponse:
        """
        Generate a signed URL for private file access
        
        Args:
            user_id: User requesting access
            file_path: Path to the file in storage
            bucket_name: Storage bucket name
            expires_in: URL expiration time in seconds
            
        Returns:
            SignedUrlResponse with URL and expiration
        """
        try:
            # Verify user owns the file
            response = self.admin_client.table("generated_files").select("*").eq(
                "user_id", user_id
            ).eq("file_path", file_path).maybe_single().execute()
            
            if not response.data:
                raise ValueError("File not found or access denied")
            
            # Generate signed URL
            storage = self.admin_client.storage.from_(bucket_name)
            signed_url_response = storage.create_signed_url(file_path, expires_in)
            
            return SignedUrlResponse(
                signed_url=signed_url_response["signedURL"],
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    async def delete_file(
        self,
        user_id: str,
        file_id: str
    ) -> bool:
        """
        Delete a file from storage
        
        Args:
            user_id: User requesting deletion
            file_id: ID of the file to delete
            
        Returns:
            True if deletion successful
        """
        try:
            # Get file details
            response = self.admin_client.table("generated_files").select("*").eq(
                "id", file_id
            ).eq("user_id", user_id).maybe_single().execute()
            
            if not response.data:
                raise ValueError("File not found or access denied")
            
            file_data = response.data
            
            # Delete from storage
            storage = self.admin_client.storage.from_(file_data["bucket_name"])
            storage.remove([file_data["file_path"]])
            
            # Delete record
            self.admin_client.table("generated_files").delete().eq("id", file_id).execute()
            
            logger.info(f"File deleted: {file_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    async def list_user_files(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
        project_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> FileListResponse:
        """
        List files belonging to a user
        
        Args:
            user_id: User ID
            file_type: Optional filter by file type
            project_id: Optional filter by project
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            FileListResponse with list of files
        """
        try:
            query = self.admin_client.table("generated_files").select("*", count="exact").eq("user_id", user_id)
            
            if file_type:
                query = query.eq("file_type", file_type.value)
            
            if project_id:
                query = query.eq("project_id", project_id)
            
            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            files = [
                FileUploadResponse(
                    file_id=f["id"],
                    file_name=f["file_name"],
                    file_path=f["file_path"],
                    public_url=f["public_url"] or "",
                    file_type=FileType(f["file_type"]),
                    file_size=f["file_size"] or 0,
                    mime_type=f["mime_type"] or "",
                    created_at=f["created_at"]
                )
                for f in response.data
            ]
            
            return FileListResponse(
                files=files,
                total=response.count or len(files)
            )
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise Exception(f"Failed to list files: {str(e)}")
    
    async def download_file(
        self,
        user_id: str,
        file_id: str
    ) -> tuple[bytes, str, str]:
        """
        Download a file from storage
        
        Args:
            user_id: User requesting download
            file_id: ID of the file to download
            
        Returns:
            Tuple of (file_data, file_name, mime_type)
        """
        try:
            # Get file details
            response = self.admin_client.table("generated_files").select("*").eq(
                "id", file_id
            ).eq("user_id", user_id).maybe_single().execute()
            
            if not response.data:
                raise ValueError("File not found or access denied")
            
            file_data = response.data
            
            # Download from storage
            storage = self.admin_client.storage.from_(file_data["bucket_name"])
            file_bytes = storage.download(file_data["file_path"])
            
            return (
                file_bytes,
                file_data["file_name"],
                file_data["mime_type"]
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get StorageService singleton instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
