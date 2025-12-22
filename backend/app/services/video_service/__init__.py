# Video assembly & captions service
from .merger import merge_audio_and_background, VideoService, get_video_service
from .background_selector import get_background_path, get_available_backgrounds, PRESET_BACKGROUNDS
from .burn_captions import burn_captions, burn_captions_with_style

__all__ = [
    "merge_audio_and_background",
    "VideoService",
    "get_video_service",
    "get_background_path",
    "get_available_backgrounds",
    "PRESET_BACKGROUNDS",
    "burn_captions",
    "burn_captions_with_style",
]
