"""
Input Layer Service - Orchestrates scraping and content processing
"""
from loguru import logger
from typing import List

from app.models.input import InputSource, ScrapedContent
from app.services.scrapers import (
    RedditScraper,
    TwitterScraper,
    StackOverflowScraper,
    BaseScraper
)


class InputService:
    """Main service for input layer operations"""
    
    def __init__(self):
        self.scrapers = {
            InputSource.REDDIT: RedditScraper(),
            InputSource.TWITTER: TwitterScraper(),
            InputSource.STACKOVERFLOW: StackOverflowScraper()
        }
    
    async def scrape_content(self, source: InputSource, url: str) -> ScrapedContent:
        """
        Scrape content from a given source and URL
        
        Args:
            source: The input source type
            url: The URL to scrape
            
        Returns:
            ScrapedContent object
            
        Raises:
            ValueError: If source is not supported
            Exception: If scraping fails
        """
        scraper = self.scrapers.get(source)
        
        if not scraper:
            raise ValueError(f"Unsupported source: {source}")
        
        logger.info(f"Scraping {source} content from: {url}")
        scraped_data = await scraper.scrape(url)
        logger.info(f"Successfully scraped {source} content: {scraped_data.title}")
        
        return scraped_data
    
    def create_content_from_script(self, script: str) -> ScrapedContent:
        """
        Create ScrapedContent from direct script input
        
        Args:
            script: The script text
            
        Returns:
            ScrapedContent object
        """
        from datetime import datetime
        
        if not script or len(script.strip()) == 0:
            raise ValueError("Script cannot be empty")
        
        # Limit script length
        if len(script) > 10000:
            logger.warning("Script exceeds 10000 characters, truncating")
            script = script[:10000]
        
        logger.info("Creating content from script input")
        
        return ScrapedContent(
            source=InputSource.SCRIPT,
            url=None,
            title="Custom Script",
            author=None,
            content=script,
            comments=[],
            metadata={
                "length": len(script),
                "word_count": len(script.split())
            }
        )
    
    async def scrape_multiple(self, requests: List[dict]) -> List[ScrapedContent]:
        """
        Scrape multiple URLs concurrently
        
        Args:
            requests: List of dicts with 'source' and 'url' keys
            
        Returns:
            List of ScrapedContent objects
        """
        import asyncio
        
        logger.info(f"Scraping {len(requests)} URLs concurrently")
        
        async def scrape_one(req: dict):
            try:
                return await self.scrape_content(
                    InputSource(req['source']),
                    req['url']
                )
            except Exception as e:
                logger.error(f"Failed to scrape {req['url']}: {str(e)}")
                return None
        
        results = await asyncio.gather(*[scrape_one(req) for req in requests])
        successful = [r for r in results if r is not None]
        
        logger.info(f"Successfully scraped {len(successful)}/{len(requests)} URLs")
        return successful
    
    def get_scraper_for_source(self, source: InputSource) -> BaseScraper:
        """
        Get the appropriate scraper for a source
        
        Args:
            source: The input source
            
        Returns:
            BaseScraper instance
        """
        scraper = self.scrapers.get(source)
        if not scraper:
            raise ValueError(f"Unsupported source: {source}")
        return scraper

