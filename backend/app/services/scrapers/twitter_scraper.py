"""
Twitter/X scraper using Tweepy
"""
import re
from typing import List, Optional
import tweepy
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.models.input import ScrapedContent, PostComment, InputSource
from .base_scraper import BaseScraper


class TwitterScraper(BaseScraper):
    """Scraper for Twitter/X threads"""
    
    def __init__(self):
        super().__init__(InputSource.TWITTER)
        self._api = None
        self._client = None
    
    @property
    def api(self):
        """Lazy initialization of Twitter API v1.1 client"""
        if self._api is None:
            if not all([
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            ]):
                raise ValueError("Twitter v1.1 credentials not configured")
            
            auth = tweepy.OAuth1UserHandler(
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            )
            self._api = tweepy.API(auth, wait_on_rate_limit=True)
        
        return self._api
    
    @property
    def client(self):
        """Lazy initialization of Twitter API v2 client"""
        if self._client is None:
            if not settings.twitter_bearer_token:
                raise ValueError("Twitter Bearer Token not configured")
            
            self._client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                wait_on_rate_limit=True
            )
        
        return self._client
    
    def validate_url(self, url: str) -> bool:
        """Validate Twitter/X URL"""
        # Supports both twitter.com and x.com
        twitter_pattern = r'https?://(www\.)?(twitter|x)\.com/.+/status/\d+'
        return bool(re.match(twitter_pattern, url))
    
    async def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape Twitter/X thread content
        
        Args:
            url: Twitter/X thread URL
            
        Returns:
            ScrapedContent object
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid Twitter/X URL: {url}")
        
        try:
            logger.info(f"Scraping Twitter thread: {url}")
            
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id(url)
            
            # Fetch tweet using API v2
            tweet_response = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            if not tweet_response.data:
                raise ValueError(f"Tweet {tweet_id} not found")
            
            tweet = tweet_response.data
            author = tweet_response.includes.get('users', [{}])[0] if tweet_response.includes else {}
            
            # Try to get thread replies using search
            thread_tweets = await self._get_thread(tweet_id)
            
            # Build metadata
            metadata = {
                "tweet_id": tweet_id,
                "retweets": tweet.public_metrics.get('retweet_count', 0),
                "likes": tweet.public_metrics.get('like_count', 0),
                "replies": tweet.public_metrics.get('reply_count', 0),
                "author_username": author.get('username', 'unknown')
            }
            
            return ScrapedContent(
                source=InputSource.TWITTER,
                url=url,
                title=f"Twitter Thread by @{metadata['author_username']}",
                author=metadata['author_username'],
                content=tweet.text,
                comments=thread_tweets,
                metadata=metadata
            )
            
        except tweepy.TooManyRequests:
            logger.error("Twitter API rate limit exceeded")
            raise Exception("Rate limit exceeded. Please try again later.")
        except Exception as e:
            logger.error(f"Error scraping Twitter: {str(e)}")
            raise Exception(f"Failed to scrape Twitter thread: {str(e)}")
    
    def _extract_tweet_id(self, url: str) -> str:
        """Extract tweet ID from URL"""
        match = re.search(r'/status/(\d+)', url)
        if not match:
            raise ValueError(f"Could not extract tweet ID from: {url}")
        return match.group(1)
    
    async def _get_thread(self, tweet_id: str, max_thread_length: int = 20) -> List[PostComment]:
        """
        Get Twitter thread replies (conversation thread)
        
        Args:
            tweet_id: Original tweet ID
            max_thread_length: Maximum number of tweets to fetch
            
        Returns:
            List of PostComment objects representing thread replies
        """
        thread = []
        
        try:
            # Get conversation ID and fetch thread
            # Note: Getting full threads is complex with Twitter API v2
            # This is a simplified version
            conversation_response = self.client.get_tweet(
                tweet_id,
                tweet_fields=['conversation_id'],
                expansions=['conversation_id']
            )
            
            if not conversation_response.data:
                return thread
            
            conversation_id = conversation_response.data.conversation_id
            
            # Search for tweets in conversation
            # Note: This might not capture all replies due to API limitations
            search_response = self.client.search_recent_tweets(
                query=f"conversation_id:{conversation_id}",
                max_results=min(max_thread_length, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'text'],
                expansions=['author_id']
            )
            
            if not search_response.data:
                return thread
            
            # Process tweets
            authors = {user.id: user.username for user in search_response.includes.get('users', [])}
            
            for idx, tweet in enumerate(search_response.data[:max_thread_length]):
                post_comment = PostComment(
                    id=tweet.id,
                    author=authors.get(tweet.author_id, 'unknown'),
                    content=self._clean_text(tweet.text),
                    upvotes=tweet.public_metrics.get('like_count', 0),
                    timestamp=tweet.created_at
                )
                thread.append(post_comment)
                
        except Exception as e:
            logger.warning(f"Could not fetch full thread: {str(e)}")
        
        return thread

