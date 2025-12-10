"""
Base scraper class defining the interface for all scrapers
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.models import ScrapedContent, InputSource


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, source: InputSource):
        self.source = source
    
    @abstractmethod
    async def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape content from the given URL
        
        Args:
            url: The URL to scrape
            
        Returns:
            ScrapedContent object with the scraped data
            
        Raises:
            ValueError: If URL is invalid or inaccessible
            Exception: For any scraping errors
        """
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is appropriate for this scraper
        
        Args:
            url: The URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = " ".join(text.split())
        return text.strip()

