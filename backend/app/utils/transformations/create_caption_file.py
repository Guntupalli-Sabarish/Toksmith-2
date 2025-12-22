"""
Caption file creation utilities for video processing.
Generates SRT subtitle files from script data.
"""
from datetime import timedelta
import os
from uuid import uuid4
from typing import Dict, Any, List
from loguru import logger


def format_srt_time(seconds: float) -> str:
    """
    Format seconds to SRT time format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string in SRT format
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def create_caption_file(script_data: Dict[str, Any], project_id: str, output_dir: str = "static/captions") -> str:
    """
    Create a caption file (SRT) from the script data.
    Uses 'dialogue_lines' or 'lines' with 'start_time' and 'duration' to compute end time.
    
    Args:
        script_data: Script data containing lines with text, start_time, and duration
        project_id: Project ID for naming the file
        output_dir: Directory to save caption files
        
    Returns:
        Path to the created SRT file
    """
    # Get lines from script data (support both formats)
    lines = script_data.get("dialogue_lines", script_data.get("lines", []))
    
    if not lines:
        logger.warning(f"No lines found in script data for project {project_id}")
        return ""
    
    srt_lines = []
    current_time = 0.0
    
    for idx, item in enumerate(lines, start=1):
        start = item.get("start_time", current_time)
        duration = item.get("duration", 3.0)  # Default 3 seconds if not specified
        end = start + duration
        
        start_time = format_srt_time(start)
        end_time = format_srt_time(end)
        text = item.get("text", "")
        
        if text.strip():  # Only add non-empty lines
            srt_lines.append(f"{idx}\n{start_time} --> {end_time}\n{text}\n")
        
        current_time = end
    
    srt_content = "\n".join(srt_lines)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    caption_file_path = os.path.join(output_dir, f"{project_id}_{uuid4().hex[:8]}.srt")
    
    with open(caption_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    logger.info(f"Caption file created: {caption_file_path}")
    return caption_file_path


def estimate_line_duration(text: str, words_per_minute: int = 150) -> float:
    """
    Estimate the duration of a line based on word count.
    
    Args:
        text: The text to estimate duration for
        words_per_minute: Speaking rate (default 150 WPM)
        
    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    duration = (word_count / words_per_minute) * 60
    return max(1.0, duration)  # Minimum 1 second
