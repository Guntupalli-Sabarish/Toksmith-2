"""
Storage API Routes
Handles file uploads, downloads, and management
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO
from loguru import logger

from app.schemas.storage import (
    FileType,
    FileUploadResponse,
    FileListResponse,
    SignedUrlRequest,
    SignedUrlResponse
)
from app.services.storage_service.storage import get_storage_service, StorageService
from app.core.dependencies import get_current_user, CurrentUser


router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Upload a file to storage"
)
async def upload_file(
    file: UploadFile = File(...),
    file_type: FileType = Query(..., description="Type of file being uploaded"),
    project_id: Optional[str] = Query(None, description="Associated project ID"),
    make_public: bool = Query(False, description="Make file publicly accessible"),
    current_user: CurrentUser = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Upload a file to Supabase Storage.
    
    - **file**: The file to upload
    - **file_type**: Type of file (video, audio, image, etc.)
    - **project_id**: Optional project to associate with
    - **make_public**: Whether to generate a public URL
    """
    try:
        # Read file data
        file_data = await file.read()
        
        result = await storage_service.upload_file(
            user_id=current_user.id,
            file_data=file_data,
            file_name=file.filename or "unnamed",
            file_type=file_type,
            mime_type=file.content_type or "application/octet-stream",
            project_id=project_id,
            make_public=make_public
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.get(
    "/files",
    response_model=FileListResponse,
    summary="List files",
    description="List all files for the current user"
)
async def list_files(
    file_type: Optional[FileType] = Query(None, description="Filter by file type"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: CurrentUser = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """List all files belonging to the current user"""
    try:
        result = await storage_service.list_user_files(
            user_id=current_user.id,
            file_type=file_type,
            project_id=project_id,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"List files error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@router.get(
    "/files/{file_id}/download",
    summary="Download file",
    description="Download a file by ID"
)
async def download_file(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Download a file"""
    try:
        file_bytes, file_name, mime_type = await storage_service.download_file(
            user_id=current_user.id,
            file_id=file_id
        )
        
        return StreamingResponse(
            BytesIO(file_bytes),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"'
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )


@router.post(
    "/files/{file_id}/signed-url",
    response_model=SignedUrlResponse,
    summary="Get signed URL",
    description="Generate a signed URL for temporary file access"
)
async def get_signed_url(
    file_id: str,
    expires_in: int = Query(3600, ge=60, le=604800, description="Expiration time in seconds"),
    current_user: CurrentUser = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Generate a signed URL for temporary file access"""
    try:
        # First get file details to get path and bucket
        files = await storage_service.list_user_files(
            user_id=current_user.id,
            limit=1000
        )
        
        file_info = None
        for f in files.files:
            if f.file_id == file_id:
                file_info = f
                break
        
        if not file_info:
            raise ValueError("File not found")
        
        # Get file record from DB to get bucket name
        from app.core.supabase import get_supabase_admin
        client = get_supabase_admin()
        response = client.table("generated_files").select("bucket_name").eq(
            "id", file_id
        ).maybe_single().execute()
        
        if not response.data:
            raise ValueError("File not found")
        
        result = await storage_service.get_signed_url(
            user_id=current_user.id,
            file_path=file_info.file_path,
            bucket_name=response.data["bucket_name"],
            expires_in=expires_in
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signed URL error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate signed URL"
        )


@router.delete(
    "/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
    description="Delete a file from storage"
)
async def delete_file(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Delete a file"""
    try:
        await storage_service.delete_file(
            user_id=current_user.id,
            file_id=file_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Delete file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
