"""
Caption Burning Service
Burns subtitles/captions into video files using FFmpeg.
"""
import os
import shutil
from typing import Optional
from loguru import logger

from app.utils.ffmpeg_utils import run_ffmpeg
from app.core.config import settings


def burn_captions(
    video_in: str,
    captions_file: Optional[str],
    output_path: str
) -> str:
    """
    Burn subtitles into a video file using FFmpeg subtitles filter.
    
    Args:
        video_in: Input video path
        captions_file: Path to SRT caption file (optional)
        output_path: Output video path
        
    Returns:
        Path to the output video
    """
    if not captions_file or not os.path.exists(captions_file):
        # No captions; just copy input to output
        logger.info("No captions file provided, copying video without captions")
        shutil.copy(video_in, output_path)
        return output_path
    
    # Escape the path for FFmpeg subtitles filter
    # Windows paths need special handling
    escaped_srt = captions_file.replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-i", video_in,
        "-vf", f"subtitles='{escaped_srt}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]
    
    try:
        run_ffmpeg(cmd)
        logger.info(f"Captions burned successfully: {output_path}")
    except Exception as e:
        logger.error(f"Failed to burn captions: {e}")
        # Fallback: copy without captions
        shutil.copy(video_in, output_path)
    
    return output_path


def burn_captions_with_style(
    video_in: str,
    captions_file: Optional[str],
    output_path: str,
    font_name: str = "Arial",
    font_size: int = 24,
    font_color: str = "white",
    outline_color: str = "black",
    outline_width: int = 2,
    position: str = "bottom"
) -> str:
    """
    Burn captions with custom styling.
    
    Args:
        video_in: Input video path
        captions_file: Path to SRT caption file
        output_path: Output video path
        font_name: Font family name
        font_size: Font size in pixels
        font_color: Text color
        outline_color: Outline/border color
        outline_width: Outline width
        position: Caption position (top, middle, bottom)
        
    Returns:
        Path to the output video
    """
    if not captions_file or not os.path.exists(captions_file):
        shutil.copy(video_in, output_path)
        return output_path
    
    # Build style string for ASS format
    # Position mapping
    alignment = {"top": 8, "middle": 5, "bottom": 2}.get(position, 2)
    
    # Escape the path
    escaped_srt = captions_file.replace("\\", "/").replace(":", "\\:")
    
    # Build subtitles filter with force_style
    style = f"FontName={font_name},FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline={outline_width},Alignment={alignment}"
    
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-i", video_in,
        "-vf", f"subtitles='{escaped_srt}':force_style='{style}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]
    
    try:
        run_ffmpeg(cmd)
        logger.info(f"Styled captions burned: {output_path}")
    except Exception as e:
        logger.error(f"Failed to burn styled captions: {e}")
        # Fallback to simple burning
        return burn_captions(video_in, captions_file, output_path)
    
    return output_path
