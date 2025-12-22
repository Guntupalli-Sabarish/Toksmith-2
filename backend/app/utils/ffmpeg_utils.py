# FFmpeg utilities for video processing
import subprocess
import os
import tempfile
import re
from typing import List
from loguru import logger

from app.core.config import settings


def run_ffmpeg(cmd: List[str]):
    """
    Run ffmpeg command synchronously and raise if failed.
    """
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        error_msg = proc.stderr.decode('utf-8')
        logger.error(f"FFmpeg failed: {error_msg}")
        raise RuntimeError(f"FFmpeg failed: {error_msg}")
    return proc


def probe_duration(path: str) -> float:
    """
    Get the duration of an audio/video file using ffprobe.
    
    Args:
        path: Path to the media file
        
    Returns:
        Duration in seconds as float
    """
    cmd = [
        settings.ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.decode("utf-8"))
    return float(res.stdout.decode().strip())


def concatenate_audio_files(audio_dir: str, output_path: str) -> str:
    """
    Concatenate all audio files in a directory into a single audio file.
    Files are sorted by their index in the filename (e.g., script_xxx_0_yyy.mp3).
    
    Args:
        audio_dir: Directory containing audio files
        output_path: Path for the concatenated output file
        
    Returns:
        Path to the concatenated audio file
    """
    if not os.path.isdir(audio_dir):
        raise ValueError(f"Audio directory does not exist: {audio_dir}")
    
    # Get all audio files and sort them by index
    audio_files = []
    for f in os.listdir(audio_dir):
        if f.endswith(('.mp3', '.wav', '.m4a', '.aac')):
            audio_files.append(f)
    
    if not audio_files:
        raise ValueError(f"No audio files found in directory: {audio_dir}")
    
    # Sort by index (extract number after second underscore)
    # Format: script_{project_id}_{index}_{hash}.mp3
    def extract_index(filename: str) -> int:
        match = re.search(r'_(\d+)_[a-f0-9]+\.(mp3|wav|m4a|aac)$', filename)
        if match:
            return int(match.group(1))
        return 0
    
    audio_files.sort(key=extract_index)
    logger.info(f"Concatenating {len(audio_files)} audio files")
    
    # Create a temporary file list for ffmpeg concat demuxer
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        concat_list_path = f.name
        for audio_file in audio_files:
            full_path = os.path.abspath(os.path.join(audio_dir, audio_file))
            # Escape single quotes in file path for ffmpeg
            escaped_path = full_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Concatenate using ffmpeg concat demuxer
        cmd = [
            settings.ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            output_path
        ]
        run_ffmpeg(cmd)
        logger.info(f"Audio concatenated to: {output_path}")
        return output_path
    finally:
        # Clean up temp file
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)


def create_silent_audio(duration: float, output_path: str) -> str:
    """
    Create a silent audio file of specified duration.
    
    Args:
        duration: Duration in seconds
        output_path: Path for the output file
        
    Returns:
        Path to the created audio file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(duration),
        "-c:a", "libmp3lame",
        output_path
    ]
    run_ffmpeg(cmd)
    return output_path
