"""
Background Video Selector
Handles selection of background videos for video generation.
"""
import os
import shutil
from typing import Optional
from loguru import logger

from app.core.config import settings


# Registry of preset background videos
PRESET_BACKGROUNDS = {
    "minecraft-parkour": "minecraft_parkour.mp4",
    "subway-surfers": "subway_surfers.mp4",
    "satisfying": "satisfying.mp4",
    "nature": "nature.mp4",
    "abstract": "abstract.mp4",
    "gaming": "gaming.mp4",
}

DEFAULT_BACKGROUND = "minecraft-parkour"


def get_available_backgrounds() -> list[str]:
    """
    Get list of available background presets.
    
    Returns:
        List of background preset names
    """
    return list(PRESET_BACKGROUNDS.keys())


def get_background_path(choice: Optional[str] = None) -> str:
    """
    Get the path to a background video.
    
    Args:
        choice: Background preset name or None for default
        
    Returns:
        Path to the background video file
    """
    background_dir = os.path.join(settings.local_storage_path, "backgrounds")
    
    # Use default if not specified
    if not choice:
        choice = DEFAULT_BACKGROUND
    
    # Check if it's a preset
    if choice in PRESET_BACKGROUNDS:
        filename = PRESET_BACKGROUNDS[choice]
        path = os.path.join(background_dir, filename)
        
        if os.path.exists(path):
            return path
        else:
            logger.warning(f"Background preset '{choice}' file not found: {path}")
    
    # Check if choice is a direct path
    if os.path.exists(choice):
        return choice
    
    # Check in backgrounds directory
    direct_path = os.path.join(background_dir, choice)
    if os.path.exists(direct_path):
        return direct_path
    
    # Add .mp4 extension and try again
    with_ext = os.path.join(background_dir, f"{choice}.mp4")
    if os.path.exists(with_ext):
        return with_ext
    
    raise FileNotFoundError(f"Background video not found: {choice}")


def create_fallback_background(output_path: str, duration: float = 10.0) -> str:
    """
    Create a simple fallback background video (solid color).
    
    Args:
        output_path: Path to save the fallback video
        duration: Duration of the video in seconds
        
    Returns:
        Path to the created video
    """
    from app.utils.ffmpeg_utils import run_ffmpeg
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1080x1920:d={duration}",
        "-vf", "format=yuv420p",
        "-c:v", "libx264",
        "-preset", "fast",
        output_path
    ]
    run_ffmpeg(cmd)
    
    logger.info(f"Created fallback background: {output_path}")
    return output_path
