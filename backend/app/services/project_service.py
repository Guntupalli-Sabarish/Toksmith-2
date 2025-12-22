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
    
    async def generate_audio(
        self,
        project_id: str,
        user_id: str,
        tts_service: "TTSService"
    ) -> ProjectResponse:
        """
        Generate audio for the project's script using TTS and upload to Supabase Storage
        
        Args:
            project_id: Project ID
            user_id: User ID
            tts_service: TTS Service instance
            
        Returns:
            Updated ProjectResponse with audio URLs
        """
        from app.models.script import Script, DialogueLine
        from app.schemas.storage import FileType
        
        try:
            # Get project
            project = await self.get_project(project_id, user_id)
            if not project:
                raise ValueError("Project not found")
            
            if not project.script_data:
                raise ValueError("No script available. Generate script first.")
            
            script_data = project.script_data
            
            # Reconstruct Script object from stored data
            lines = [
                DialogueLine(
                    speaker=line.get("speaker", "Narrator"),
                    text=line.get("text", ""),
                    audio_file_path=line.get("audio_file_path", ""),
                    start_time=line.get("start_time", 0),
                    duration=line.get("duration", 0)
                )
                for line in script_data.get("dialogue_lines", script_data.get("lines", []))
            ]
            
            script = Script(
                id=script_data.get("id", f"script_{project_id}"),
                lines=lines,
                background=script_data.get("background", "minecraft-parkour"),
                characters=script_data.get("characters", [])
            )
            
            # Generate audio bytes
            logger.info(f"Generating audio for project: {project_id}")
            audio_results = await tts_service.generate_script_audio_bytes(script)
            
            # Upload each audio file to Supabase Storage
            audio_urls = []
            updated_lines = list(script.lines)
            
            for line_index, audio_bytes, filename in audio_results:
                try:
                    # Upload to Supabase Storage
                    file_path = f"{user_id}/{project_id}/audio/{filename}"
                    bucket_name = settings.storage_bucket_audio
                    
                    storage = self.client.storage.from_(bucket_name)
                    storage.upload(
                        path=file_path,
                        file=audio_bytes,
                        file_options={"content-type": "audio/mpeg"}
                    )
                    
                    # Get public URL
                    public_url = storage.get_public_url(file_path)
                    audio_urls.append(public_url)
                    
                    # Update the line with the URL
                    if line_index < len(updated_lines):
                        updated_lines[line_index].audio_file_path = public_url
                    
                    logger.info(f"Uploaded audio {line_index}: {public_url}")
                    
                except Exception as upload_error:
                    logger.error(f"Failed to upload audio for line {line_index}: {upload_error}")
                    # Continue with other files
            
            # Combine all audio URLs for the main audio_url field
            # Use the first audio or create a combined reference
            main_audio_url = audio_urls[0] if audio_urls else None
            
            # Update script_data with audio URLs
            updated_script_data = {
                "id": script.id,
                "background": script.background,
                "characters": script.characters,
                "dialogue_lines": [
                    {
                        "speaker": updated_lines[i].speaker if i < len(updated_lines) else line.speaker,
                        "text": updated_lines[i].text if i < len(updated_lines) else line.text,
                        "audio_file_path": updated_lines[i].audio_file_path if i < len(updated_lines) else "",
                        "start_time": updated_lines[i].start_time if i < len(updated_lines) else 0,
                        "duration": updated_lines[i].duration if i < len(updated_lines) else 0
                    }
                    for i, line in enumerate(script_data.get("dialogue_lines", script_data.get("lines", [])))
                ],
                "estimated_duration": script_data.get("estimated_duration", 0),
                "word_count": script_data.get("word_count", 0),
                "audio_urls": audio_urls  # Store all audio URLs
            }
            
            # Update project with audio URL and script data
            response = self.client.table("projects").update({
                "status": ProjectStatus.AUDIO_GENERATED.value,
                "script_data": updated_script_data,
                "audio_url": main_audio_url  # Store first audio URL as main
            }).eq("id", project_id).execute()
            
            logger.info(f"Audio generated and uploaded for project: {project_id}")
            return self._map_to_response(response.data[0])
            
        except ValueError:
            raise
        except Exception as e:
            # Update status to failed
            self.client.table("projects").update({
                "status": ProjectStatus.FAILED.value,
                "error_message": str(e)
            }).eq("id", project_id).execute()
            
            logger.error(f"Failed to generate audio: {str(e)}")
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    async def generate_video(
        self,
        project_id: str,
        user_id: str,
        background: str = "minecraft-parkour"
    ) -> ProjectResponse:
        """
        Generate video for the project by combining audio with background and captions.
        
        Args:
            project_id: Project ID
            user_id: User ID
            background: Background video preset or path
            
        Returns:
            Updated ProjectResponse with video URL
        """
        from app.utils.ffmpeg_utils import concatenate_audio_files
        from app.utils.transformations import create_caption_file
        from app.services.video_service import merge_audio_and_background
        import tempfile
        import os
        
        try:
            # Get project
            project = await self.get_project(project_id, user_id)
            if not project:
                raise ValueError("Project not found")
            
            if project.status != ProjectStatus.AUDIO_GENERATED:
                raise ValueError("Audio must be generated before video creation")
            
            script_data = project.script_data
            if not script_data:
                raise ValueError("No script data found")
            
            logger.info(f"Generating video for project: {project_id}")
            
            # Create temp directory for local processing
            with tempfile.TemporaryDirectory(prefix="toksmith_video_") as tmp_dir:
                # Download audio files from Supabase and concatenate
                audio_urls = script_data.get("audio_urls", [])
                
                if not audio_urls:
                    raise ValueError("No audio files found in project")
                
                # Download audio files
                local_audio_dir = os.path.join(tmp_dir, "audio")
                os.makedirs(local_audio_dir, exist_ok=True)
                
                import httpx
                for i, url in enumerate(audio_urls):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url)
                        if response.status_code == 200:
                            audio_path = os.path.join(local_audio_dir, f"audio_{i:03d}.mp3")
                            with open(audio_path, "wb") as f:
                                f.write(response.content)
                
                # Concatenate audio files
                concatenated_audio = os.path.join(tmp_dir, "combined_audio.mp3")
                concatenate_audio_files(local_audio_dir, concatenated_audio)
                
                # Create caption file
                caption_file = create_caption_file(
                    script_data=script_data,
                    project_id=project_id,
                    output_dir=tmp_dir
                )
                
                # Generate video
                video_output_dir = os.path.join(tmp_dir, "output")
                os.makedirs(video_output_dir, exist_ok=True)
                
                video_path = merge_audio_and_background(
                    background_video=background,
                    audio_file=concatenated_audio,
                    captions_srt=caption_file if caption_file else None,
                    project_id=project_id,
                    output_dir=video_output_dir
                )
                
                # Upload video to Supabase Storage
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                
                video_filename = f"{project_id}_final.mp4"
                video_storage_path = f"{user_id}/{project_id}/video/{video_filename}"
                
                bucket_name = settings.storage_bucket_videos
                storage = self.client.storage.from_(bucket_name)
                storage.upload(
                    path=video_storage_path,
                    file=video_bytes,
                    file_options={"content-type": "video/mp4"}
                )
                
                video_url = storage.get_public_url(video_storage_path)
                
                logger.info(f"Video uploaded: {video_url}")
            
            # Update project with video URL
            response = self.client.table("projects").update({
                "status": ProjectStatus.VIDEO_GENERATED.value,
                "video_url": video_url
            }).eq("id", project_id).execute()
            
            logger.info(f"Video generated for project: {project_id}")
            return self._map_to_response(response.data[0])
            
        except ValueError:
            raise
        except Exception as e:
            # Update status to failed
            self.client.table("projects").update({
                "status": ProjectStatus.FAILED.value,
                "error_message": str(e)
            }).eq("id", project_id).execute()
            
            logger.error(f"Failed to generate video: {str(e)}")
            raise Exception(f"Failed to generate video: {str(e)}")
    
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
