"""
Video Merger Service
Combines background video, audio, and captions into final video output.
"""
import os
import tempfile
import shutil
from typing import Optional
from loguru import logger

from app.utils.ffmpeg_utils import probe_duration, run_ffmpeg
from app.core.config import settings


def merge_audio_and_background(
    background_video: str,
    audio_file: str,
    captions_srt: Optional[str] = None,
    project_id: Optional[str] = None,
    output_dir: str = "static/videos"
) -> str:
    """
    Merge background video with audio and optionally burn captions.
    
    Pipeline:
    1. Ensure background video length matches audio length (loop/pad/trim)
    2. Optionally burn captions
    3. Mix audio + final video -> output
    
    Args:
        background_video: Path or name of background video file
        audio_file: Path to the audio file
        captions_srt: Optional path to SRT caption file
        project_id: Project ID for output naming
        output_dir: Directory to save output video
        
    Returns:
        Path to the final merged video
    """
    tmp_dir = tempfile.mkdtemp(prefix="tok_vid_")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine output path
        output_filename = f"{project_id}_final.mp4" if project_id else "final_video.mp4"
        out_path = os.path.join(output_dir, output_filename)
        
        # Resolve background video path
        if not os.path.isabs(background_video):
            # Check in static/backgrounds first
            bg_path = os.path.join("static", "backgrounds", background_video)
            if not os.path.exists(bg_path):
                # Try with .mp4 extension
                bg_path = os.path.join("static", "backgrounds", f"{background_video}.mp4")
            if not os.path.exists(bg_path):
                raise FileNotFoundError(f"Background video not found: {background_video}")
            background_video = bg_path
        
        # Get durations
        audio_dur = probe_duration(audio_file)
        bg_dur = probe_duration(background_video)
        
        logger.info(f"Audio duration: {audio_dur}s, Background duration: {bg_dur}s")
        
        bg_adjusted = os.path.join(tmp_dir, "bg_adjusted.mp4")
        
        # Adjust background video to match audio duration
        if bg_dur < audio_dur:
            # Loop background video to match audio duration
            loop_count = int((audio_dur // bg_dur) + 1)
            logger.info(f"Looping background {loop_count} times")
            
            cmd = [
                settings.ffmpeg_path,
                "-y",
                "-stream_loop", str(loop_count),
                "-i", background_video,
                "-t", str(audio_dur),
                "-c", "copy",
                bg_adjusted
            ]
            run_ffmpeg(cmd)
        else:
            # Trim background to audio duration
            cmd = [
                settings.ffmpeg_path,
                "-y",
                "-i", background_video,
                "-ss", "0",
                "-t", str(audio_dur),
                "-c", "copy",
                bg_adjusted
            ]
            run_ffmpeg(cmd)
        
        # Burn captions if provided
        if captions_srt and os.path.exists(captions_srt):
            bg_with_captions = os.path.join(tmp_dir, "bg_captions.mp4")
            
            # Escape path for subtitles filter
            escaped_srt = captions_srt.replace("\\", "/").replace(":", "\\:")
            
            cmd = [
                settings.ffmpeg_path,
                "-y",
                "-i", bg_adjusted,
                "-vf", f"subtitles='{escaped_srt}'",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                bg_with_captions
            ]
            run_ffmpeg(cmd)
            final_bg = bg_with_captions
        else:
            final_bg = bg_adjusted
        
        # Merge final video with audio (replace audio track)
        cmd = [
            settings.ffmpeg_path,
            "-y",
            "-i", final_bg,
            "-i", audio_file,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            out_path
        ]
        run_ffmpeg(cmd)
        
        logger.info(f"Video merged successfully: {out_path}")
        return out_path
        
    finally:
        # Clean up temp directory
        shutil.rmtree(tmp_dir, ignore_errors=True)


def get_video_service():
    """Factory function for dependency injection."""
    return VideoService()


class VideoService:
    """Service for video generation operations."""
    
    def __init__(self):
        pass
    
    async def create_video(
        self,
        audio_file: str,
        background_video: str,
        captions_srt: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> str:
        """
        Create a video by merging audio with background and optional captions.
        
        Args:
            audio_file: Path to the concatenated audio file
            background_video: Background video identifier or path
            captions_srt: Optional path to SRT file
            project_id: Project ID
            
        Returns:
            Path to the generated video
        """
        return merge_audio_and_background(
            background_video=background_video,
            audio_file=audio_file,
            captions_srt=captions_srt,
            project_id=project_id
        )
