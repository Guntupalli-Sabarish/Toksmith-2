"""
Project Service
Handles video project CRUD operations and workflow
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from loguru import logger

from app.core.supabase import get_supabase_admin
from app.core.config import settings
from app.schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectListResponse,
    ProjectStatus,
    SourceType
)
from app.services.input_service.input_layer import InputService
from app.services.llm_service.llm_service import LLMService, RawThreadData
from app.models.input import InputSource


class ProjectService:
    """Service for handling video project operations"""
    
    def __init__(self):
        self.client = get_supabase_admin()
        self.input_service = InputService()
        self.llm_service = LLMService(api_key=settings.gemini_api_key)
    
    async def create_project(
        self, 
        user_id: str, 
        project_data: ProjectCreate
    ) -> ProjectResponse:
        """
        Create a new video project
        
        Args:
            user_id: Owner's user ID
            project_data: Project creation data
            
        Returns:
            Created ProjectResponse
        """
        try:
            # Detect source type from URL
            source_type = self._detect_source_type(project_data.source_url)
            
            # Create project record
            project_id = str(uuid.uuid4())
            
            insert_data = {
                "id": project_id,
                "user_id": user_id,
                "title": project_data.title,
                "description": project_data.description,
                "source_url": project_data.source_url,
                "source_type": source_type.value if source_type else None,
                "video_style": project_data.video_style.value,
                "status": ProjectStatus.DRAFT.value
            }
            
            response = self.client.table("projects").insert(insert_data).execute()
            
            if not response.data:
                raise Exception("Failed to create project")
            
            data = response.data[0]
            logger.info(f"Project created: {project_id} for user: {user_id}")
            
            return self._map_to_response(data)
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise Exception(f"Failed to create project: {str(e)}")
    
    async def get_project(
        self, 
        project_id: str, 
        user_id: str
    ) -> Optional[ProjectResponse]:
        """
        Get a project by ID
        
        Args:
            project_id: Project ID
            user_id: User ID (for ownership verification)
            
        Returns:
            ProjectResponse if found, None otherwise
        """
        try:
            response = self.client.table("projects").select("*").eq(
                "id", project_id
            ).eq("user_id", user_id).maybe_single().execute()
            
            if not response.data:
                return None
            
            return self._map_to_response(response.data)
            
        except Exception as e:
            logger.error(f"Failed to get project: {str(e)}")
            return None
    
    async def list_projects(
        self,
        user_id: str,
        status: Optional[ProjectStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> ProjectListResponse:
        """
        List user's projects with pagination
        
        Args:
            user_id: User ID
            status: Optional status filter
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            ProjectListResponse with projects and pagination info
        """
        try:
            offset = (page - 1) * per_page
            
            query = self.client.table("projects").select("*", count="exact").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("created_at", desc=True).range(
                offset, offset + per_page - 1
            ).execute()
            
            projects = [self._map_to_response(p) for p in response.data]
            
            return ProjectListResponse(
                projects=projects,
                total=response.count or len(projects),
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise Exception(f"Failed to list projects: {str(e)}")
    
    async def update_project(
        self,
        project_id: str,
        user_id: str,
        update_data: ProjectUpdate
    ) -> ProjectResponse:
        """
        Update a project
        
        Args:
            project_id: Project ID
            user_id: User ID (for ownership verification)
            update_data: Update data
            
        Returns:
            Updated ProjectResponse
        """
        try:
            # Build update dict
            update_dict = {
                k: v.value if hasattr(v, 'value') else v
                for k, v in update_data.model_dump().items() 
                if v is not None
            }
            
            if not update_dict:
                return await self.get_project(project_id, user_id)
            
            response = self.client.table("projects").update(
                update_dict
            ).eq("id", project_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise ValueError("Project not found")
            
            logger.info(f"Project updated: {project_id}")
            return self._map_to_response(response.data[0])
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update project: {str(e)}")
            raise Exception(f"Failed to update project: {str(e)}")
    
    async def delete_project(
        self,
        project_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            user_id: User ID (for ownership verification)
            
        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.table("projects").delete().eq(
                "id", project_id
            ).eq("user_id", user_id).execute()
            
            if not response.data:
                raise ValueError("Project not found")
            
            logger.info(f"Project deleted: {project_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete project: {str(e)}")
            raise Exception(f"Failed to delete project: {str(e)}")
    
    async def scrape_content(
        self,
        project_id: str,
        user_id: str
    ) -> ProjectResponse:
        """
        Scrape content from the project's source URL
        
        Args:
            project_id: Project ID
            user_id: User ID
            
        Returns:
            Updated ProjectResponse with scraped content
        """
        try:
            # Get project
            project = await self.get_project(project_id, user_id)
            if not project:
                raise ValueError("Project not found")
            
            if not project.source_url:
                raise ValueError("Project has no source URL")
            
            # Update status to pending
            self.client.table("projects").update({
                "status": ProjectStatus.PENDING.value
            }).eq("id", project_id).execute()
            
            # Determine source type
            source_type = self._detect_source_type(project.source_url)
            input_source = self._map_source_type_to_input(source_type)
            
            # Scrape content
            logger.info(f"Scraping content for project: {project_id}")
            scraped_content = await self.input_service.scrape_content(
                input_source, 
                project.source_url
            )
            
            # Serialize scraped content
            scraped_dict = scraped_content.model_dump()
            if scraped_dict.get("timestamp"):
                scraped_dict["timestamp"] = scraped_dict["timestamp"].isoformat()
            
            # Update project
            response = self.client.table("projects").update({
                "status": ProjectStatus.SCRAPED.value,
                "scraped_data": scraped_dict,
                "title": project.title or scraped_dict.get("title", "Untitled")
            }).eq("id", project_id).execute()
            
            logger.info(f"Content scraped for project: {project_id}")
            return self._map_to_response(response.data[0])
            
        except ValueError:
            raise
        except Exception as e:
            # Update status to failed
            self.client.table("projects").update({
                "status": ProjectStatus.FAILED.value,
                "error_message": str(e)
            }).eq("id", project_id).execute()
            
            logger.error(f"Failed to scrape content: {str(e)}")
            raise Exception(f"Failed to scrape content: {str(e)}")
    
    async def generate_script(
        self,
        project_id: str,
        user_id: str
    ) -> ProjectResponse:
        """
        Generate script from scraped content
        
        Args:
            project_id: Project ID
            user_id: User ID
            
        Returns:
            Updated ProjectResponse with generated script
        """
        try:
            # Get project
            project = await self.get_project(project_id, user_id)
            if not project:
                raise ValueError("Project not found")
            
            if not project.scraped_data:
                raise ValueError("No scraped content available. Scrape content first.")
            
            scraped_data = project.scraped_data
            
            # Convert to RawThreadData format
            raw_thread = RawThreadData(
                title=scraped_data.get("title", ""),
                content=scraped_data.get("content", ""),
                author=scraped_data.get("author", "Anonymous"),
                subreddit=scraped_data.get("metadata", {}).get("subreddit", "content"),
                upvotes=scraped_data.get("metadata", {}).get("upvotes", 0),
                comments=[
                    {
                        "author": c.get("author"),
                        "content": c.get("content"),
                        "upvotes": c.get("upvotes", 0)
                    }
                    for c in scraped_data.get("comments", [])
                ]
            )
            
            # Generate script
            logger.info(f"Generating script for project: {project_id}")
            script = await self.llm_service.generate_structured_script(raw_thread)
            
            # Update project with script data
            # The Script model has: id, lines, background, characters
            script_data = {
                "id": script.id,
                "background": script.background,
                "characters": script.characters,
                "dialogue_lines": [
                    {
                        "speaker": line.speaker,
                        "text": line.text,
                        "audio_file_path": line.audio_file_path,
                        "start_time": line.start_time,
                        "duration": line.duration
                    }
                    for line in script.lines
                ],
                "estimated_duration": sum(line.duration for line in script.lines) if script.lines else 0,
                "word_count": sum(len(line.text.split()) for line in script.lines) if script.lines else 0
            }
            
            response = self.client.table("projects").update({
                "status": ProjectStatus.SCRIPT_GENERATED.value,
                "script_data": script_data
            }).eq("id", project_id).execute()
            
            logger.info(f"Script generated for project: {project_id}")
            return self._map_to_response(response.data[0])
            
        except ValueError:
            raise
        except Exception as e:
            # Update status to failed
            self.client.table("projects").update({
                "status": ProjectStatus.FAILED.value,
                "error_message": str(e)
            }).eq("id", project_id).execute()
            
            logger.error(f"Failed to generate script: {str(e)}")
            raise Exception(f"Failed to generate script: {str(e)}")
    
    def _detect_source_type(self, url: str) -> Optional[SourceType]:
        """Detect source type from URL"""
        url_lower = url.lower()
        
        if "reddit.com" in url_lower:
            return SourceType.REDDIT
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return SourceType.TWITTER
        elif "stackoverflow.com" in url_lower:
            return SourceType.STACKOVERFLOW
        else:
            return SourceType.CUSTOM
    
    def _map_source_type_to_input(self, source_type: Optional[SourceType]) -> InputSource:
        """Map SourceType to InputSource enum"""
        mapping = {
            SourceType.REDDIT: InputSource.REDDIT,
            SourceType.TWITTER: InputSource.TWITTER,
            SourceType.STACKOVERFLOW: InputSource.STACKOVERFLOW,
            SourceType.CUSTOM: InputSource.CUSTOM
        }
        return mapping.get(source_type, InputSource.REDDIT)
    
    def _map_to_response(self, data: Dict[str, Any]) -> ProjectResponse:
        """Map database record to ProjectResponse"""
        return ProjectResponse(
            id=data["id"],
            user_id=data["user_id"],
            title=data.get("title"),
            description=data.get("description"),
            source_url=data.get("source_url"),
            source_type=SourceType(data["source_type"]) if data.get("source_type") else None,
            video_style=data.get("video_style", "tiktok"),
            status=ProjectStatus(data.get("status", "draft")),
            scraped_data=data.get("scraped_data"),
            script_data=data.get("script_data"),
            video_url=data.get("video_url"),
            audio_url=data.get("audio_url"),
            thumbnail_url=data.get("thumbnail_url"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


# Singleton instance
_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """Get ProjectService singleton instance"""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service
