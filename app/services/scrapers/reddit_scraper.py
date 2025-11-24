"""
Reddit scraper using PRAW (Python Reddit API Wrapper)
"""
import re
from typing import List
from praw import Reddit
from praw.models import Submission, Comment
from loguru import logger

from app.core.config import settings
from app.models.input import ScrapedContent, PostComment, InputSource
from .base_scraper import BaseScraper


class RedditScraper(BaseScraper):
    """Scraper for Reddit threads"""
    
    def __init__(self):
        super().__init__(InputSource.REDDIT)
        self._client = None
    
    @property
    def client(self) -> Reddit:
        """Lazy initialization of Reddit client"""
        if self._client is None:
            if not settings.reddit_client_id or not settings.reddit_client_secret:
                raise ValueError("Reddit credentials not configured")
            
            self._client = Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
        return self._client
    
    def validate_url(self, url: str) -> bool:
        """Validate Reddit URL"""
        reddit_pattern = r'https?://(www\.)?reddit\.com/r/[^/]+/comments/[a-z0-9]+'
        return bool(re.match(reddit_pattern, url))
    
    async def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape Reddit thread content
        
        Args:
            url: Reddit thread URL
            
        Returns:
            ScrapedContent object
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid Reddit URL: {url}")
        
        try:
            logger.info(f"Scraping Reddit thread: {url}")
            
            # Extract submission from URL
            submission = self.client.submission(url=url)
            submission.comments.replace_more(limit=0)  # Remove 'more comments' placeholders
            
            # Get top-level comments
            comments = self._extract_comments(submission.comments)
            
            # Build metadata
            metadata = {
                "subreddit": submission.subreddit.display_name,
                "upvotes": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "url": submission.url,
                "permalink": submission.permalink
            }
            
            return ScrapedContent(
                source=InputSource.REDDIT,
                url=url,
                title=submission.title,
                author=str(submission.author) if submission.author else None,
                content=submission.selftext or submission.url,
                comments=comments,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error scraping Reddit: {str(e)}")
            raise Exception(f"Failed to scrape Reddit thread: {str(e)}")
    
    def _extract_comments(self, comments) -> List[PostComment]:
        """
        Extract comments recursively
        
        Args:
            comments: PRAW comment forest
            
        Returns:
            List of PostComment objects
        """
        result = []
        
        for comment in comments[:50]:  # Limit to top 50 comments
            if not isinstance(comment, Comment):
                continue
            
            # Skip deleted/removed comments
            if comment.body in ["[deleted]", "[removed]"]:
                continue
            
            post_comment = PostComment(
                id=comment.id,
                author=str(comment.author) if comment.author else None,
                content=self._clean_text(comment.body),
                upvotes=comment.score
            )
            
            # Recursively get replies
            if comment.replies:
                post_comment.replies = self._extract_comments(comment.replies)
            
            result.append(post_comment)
        
        return result
    
    def _get_thread_summary(self, submission: Submission, comments: List[PostComment]) -> str:
        """
        Create a summary of the thread content
        
        Args:
            submission: Reddit submission
            comments: List of comments
            
        Returns:
            Summary string
        """
        summary_parts = [submission.title]
        
        if submission.selftext:
            summary_parts.append(submission.selftext[:500])  # First 500 chars
        
        # Add top comments
        for comment in comments[:3]:
            summary_parts.append(f"Comment by {comment.author or 'Unknown'}: {comment.content[:300]}")
        
        return "\n\n".join(summary_parts)

