"""
URL validation for different sources
"""
import re
from typing import Optional
from src.models import InputSource
from loguru import logger


def validate_url(url: str, source: InputSource) -> tuple[bool, str]:
    """
    Validate URL based on source type
    
    Returns:
        (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    # Reddit validation
    if source == InputSource.REDDIT:
        pattern = r'https?://(www\.)?reddit\.com/r/[^/]+/comments/[a-z0-9]+'
        if not re.match(pattern, url):
            return False, "Invalid Reddit URL format"
        return True, ""
    
    # Twitter validation
    if source == InputSource.TWITTER:
        pattern = r'https?://(www\.)?(twitter|x)\.com/.+/status/\d+'
        if not re.match(pattern, url):
            return False, "Invalid Twitter/X URL format"
        return True, ""
    
    # StackOverflow validation
    if source == InputSource.STACKOVERFLOW:
        pattern = r'https?://stackoverflow\.com/questions/\d+/.+'
        if not re.match(pattern, url):
            return False, "Invalid StackOverflow URL format"
        return True, ""
    
    return False, f"Unsupported source: {source}"


def infer_source_from_url(url: str) -> tuple[Optional[InputSource], str]:
    """
    Try to infer the InputSource from the given URL string.

    Returns a tuple: (InputSource or None, error_message)
    """
    if not url:
        return None, "URL is required"

    # Reddit
    if re.search(r'reddit\.com/r/[^/]+/comments/[a-z0-9]+', url, re.IGNORECASE):
        return InputSource.REDDIT, ""

    # Twitter/X
    if re.search(r'(twitter|x)\.com/.+/status/\d+', url, re.IGNORECASE):
        return InputSource.TWITTER, ""

    # StackOverflow
    if re.search(r'stackoverflow\.com/questions/\d+/', url, re.IGNORECASE):
        return InputSource.STACKOVERFLOW, ""

    return None, f"Could not infer source from URL: {url}"

