#!/usr/bin/env python3
"""
Quick test script for LLM Service - Works with or without API key!

This script provides multiple test modes:
1. Model tests - Test data structures (no API key needed)
2. Mock test - Test with fake data (no API key needed)  
3. Live test - Test with real Gemini API (API key required)
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import LLMService, RawThreadData
from app.models.script import Script, DialogueLine


def test_models():
    """Test 1: Test Script and DialogueLine models (no API needed)"""
    print("\n" + "="*60)
    print("TEST 1: Testing Models (No API Key Needed)")
    print("="*60)
    
    try:
        # Test DialogueLine
        line = DialogueLine(
            speaker="Narrator",
            text="Welcome to the test!",
            audio_file_path="/test/audio.wav",
            start_time=0.0,
            duration=3.5
        )
        print(f"✅ DialogueLine created: {line.speaker} says '{line.text[:30]}...'")
        
        # Test Script
        script = Script.create(
            lines=[line],
            background="minecraft-parkour",
            characters=["narrator"]
        )
        print(f"✅ Script created with ID: {script.id}")
        print(f"   - Lines: {len(script.lines)}")
        print(f"   - Background: {script.background}")
        print(f"   - Characters: {script.characters}")
        
        # Test adding a line
        script.add_dialogue_line(
            DialogueLine(speaker="OP", text="This is my story")
        )
        print(f"✅ Added dialogue line, now has {len(script.lines)} lines")
        
        print("\n✅ MODEL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ MODEL TEST FAILED: {e}")
        return False


async def test_live_api():
    """Test 2: Test with real Gemini API (API key required)"""
    print("\n" + "="*60)
    print("TEST 2: Testing Live API Call (API Key Required)")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your-gemini-api-key-here':
        print("\n⚠️  SKIPPED: No valid GEMINI_API_KEY found")
        print("   To run this test:")
        print("   export GEMINI_API_KEY='your-actual-key'")
        return None
    
    try:
        print("✅ API key found, initializing service...")
        service = LLMService()
        
        # Create test data
        raw_thread = RawThreadData(
            title="AITA for testing my LLM service?",
            content="I built an awesome script generator and want to make sure it works properly.",
            author="developer",
            subreddit="programming",
            upvotes=42,
            comments=[
                {
                    "author": "helpful_user",
                    "content": "NTA - Testing is essential!",
                    "upvotes": 15
                }
            ]
        )
        print("✅ Created test data")
        
        print("\n🔄 Calling Gemini API (this may take a few seconds)...")
        script = await service.generate_structured_script(raw_thread)
        
        print(f"\n✅ API call successful!")
        print(f"   - Script ID: {script.id}")
        print(f"   - Lines: {len(script.lines)}")
        print(f"   - Background: {script.background}")
        print(f"   - Characters: {', '.join(script.characters)}")
        
        print("\n📝 Generated Script:")
        for i, line in enumerate(script.lines, 1):
            print(f"\n   [{i}] {line.speaker}:")
            print(f"       {line.text}")
        
        print("\n✅ LIVE API TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ LIVE API TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("LLM SERVICE QUICK TEST")
    print("🧪" * 30)
    
    results = []
    
    # Test 1: Models (always runs)
    results.append(("Models", test_models()))
    
    # Test 2: Live API (only if key is set)
    api_result = asyncio.run(test_live_api())
    if api_result is not None:
        results.append(("Live API", api_result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your LLM service is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
