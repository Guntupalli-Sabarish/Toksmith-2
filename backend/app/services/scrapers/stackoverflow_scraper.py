"""
StackOverflow scraper using web scraping
"""
import re
from typing import List
from bs4 import BeautifulSoup
import httpx
from loguru import logger

from app.models.input import ScrapedContent, PostComment, InputSource
from .base_scraper import BaseScraper


class StackOverflowScraper(BaseScraper):
    """Scraper for StackOverflow questions and answers"""
    
    def __init__(self):
        super().__init__(InputSource.STACKOVERFLOW)
        self.base_url = "https://stackoverflow.com"
    
    def validate_url(self, url: str) -> bool:
        """Validate StackOverflow URL"""
        stackoverflow_pattern = r'https?://stackoverflow\.com/questions/\d+/.+'
        return bool(re.match(stackoverflow_pattern, url))
    
    async def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape StackOverflow question and answers
        
        Args:
            url: StackOverflow question URL
            
        Returns:
            ScrapedContent object
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid StackOverflow URL: {url}")
        
        try:
            logger.info(f"Scraping StackOverflow: {url}")
            
            # Fetch HTML content
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                html = response.text
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract question title
            title_elem = soup.find('h1', class_='fs-headline1')
            title = title_elem.get_text(strip=True) if title_elem else "Untitled Question"
            
            # Extract question content
            question_elem = soup.find('div', class_='s-prose js-post-body')
            question_content = question_elem.get_text(separator='\n') if question_elem else ""
            
            # Extract author
            author_elem = soup.find('div', class_='user-details')
            author = None
            if author_elem:
                author_link = author_elem.find('a')
                if author_link:
                    author = author_link.get_text(strip=True)
            
            # Extract answers
            answers = self._extract_answers(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            return ScrapedContent(
                source=InputSource.STACKOVERFLOW,
                url=url,
                title=title,
                author=author,
                content=self._clean_text(question_content),
                comments=answers,
                metadata=metadata
            )
            
        except httpx.RequestError as e:
            logger.error(f"Network error scraping StackOverflow: {str(e)}")
            raise Exception(f"Failed to fetch StackOverflow page: {str(e)}")
        except Exception as e:
            logger.error(f"Error scraping StackOverflow: {str(e)}")
            raise Exception(f"Failed to scrape StackOverflow: {str(e)}")
    
    def _extract_answers(self, soup: BeautifulSoup) -> List[PostComment]:
        """
        Extract answers from StackOverflow page
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of PostComment objects
        """
        answers = []
        
        # Find all answer divs
        answer_divs = soup.find_all('div', class_='answer')
        
        for idx, answer_div in enumerate(answer_divs[:20]):  # Limit to top 20 answers
            # Extract answer content
            answer_content_elem = answer_div.find('div', class_='s-prose js-post-body')
            if not answer_content_elem:
                continue
            
            answer_content = answer_content_elem.get_text(separator='\n')
            
            # Extract author
            author_elem = answer_div.find('div', class_='user-details')
            author = None
            if author_elem:
                author_link = author_elem.find('a')
                if author_link:
                    author = author_link.get_text(strip=True)
            
            # Extract score
            score_elem = answer_div.find('div', class_='js-vote-count')
            score = int(score_elem.get_text(strip=True)) if score_elem else 0
            
            # Extract accepted badge
            is_accepted = answer_div.find('span', class_='accepted-answer-badge') is not None
            
            post_comment = PostComment(
                id=f"answer-{idx}",
                author=author,
                content=self._clean_text(answer_content),
                upvotes=score
            )
            
            if is_accepted:
                # Mark as most helpful
                post_comment.content = "[✅ ACCEPTED ANSWER]\n\n" + post_comment.content
            
            answers.append(post_comment)
        
        return answers
    
    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """
        Extract metadata from StackOverflow page
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        try:
            # Extract question score
            question_score_elem = soup.find('div', {'data-post-id': re.compile(r'\d+')}, class_='js-vote-count')
            if question_score_elem:
                metadata['question_score'] = int(question_score_elem.get_text(strip=True))
            
            # Extract view count
            views_elem = soup.find('div', class_='s-sidebarwidget--header')
            if views_elem:
                views_text = views_elem.get_text()
                views_match = re.search(r'(\d+)\s+times?', views_text)
                if views_match:
                    metadata['views'] = int(views_match.group(1))
            
            # Extract tags
            tags = []
            tag_elems = soup.find_all('a', class_='post-tag')
            tags = [tag.get_text(strip=True) for tag in tag_elems]
            metadata['tags'] = tags
            
        except Exception as e:
            logger.warning(f"Could not extract all metadata: {str(e)}")
        
        return metadata

