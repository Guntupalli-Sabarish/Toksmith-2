"""
Simple test example for Input Layer
This is a basic test script to verify the implementation
"""
import asyncio
from src.service import InputService
from src.models import InputSource


async def test_scrapers():
    """Test basic scraper functionality"""
    service = InputService()
    
    print("Testing Input Layer Scrapers...\n")
    
    # Test Reddit scraper
    print("Testing Reddit Scraper:")
    try:
        reddit_scraper = service.get_scraper_for_source(InputSource.REDDIT)
        print(f"✓ Reddit scraper initialized: {reddit_scraper.validate_url('https://www.reddit.com/r/test/comments/abc123')}")
    except Exception as e:
        print(f"✗ Reddit scraper error: {str(e)}")
    
    # Test Twitter scraper
    print("\nTesting Twitter Scraper:")
    try:
        twitter_scraper = service.get_scraper_for_source(InputSource.TWITTER)
        print(f"✓ Twitter scraper initialized: {twitter_scraper.validate_url('https://twitter.com/user/status/1234567890')}")
    except Exception as e:
        print(f"✗ Twitter scraper error: {str(e)}")
    
    # Test StackOverflow scraper
    print("\nTesting StackOverflow Scraper:")
    try:
        stackoverflow_scraper = service.get_scraper_for_source(InputSource.STACKOVERFLOW)
        print(f"✓ StackOverflow scraper initialized: {stackoverflow_scraper.validate_url('https://stackoverflow.com/questions/12345/test-question')}")
    except Exception as e:
        print(f"✗ StackOverflow scraper error: {str(e)}")
    
    # Test script processing
    print("\nTesting Script Processing:")
    try:
        script_content = service.create_content_from_script("This is a test script for ToksMith")
        print(f"✓ Script processed: {script_content.title} ({len(script_content.content)} chars)")
    except Exception as e:
        print(f"✗ Script processing error: {str(e)}")
    
    print("\n" + "="*50)
    print("Test completed! Configure API credentials to test live scraping.")


if __name__ == "__main__":
    asyncio.run(test_scrapers())

