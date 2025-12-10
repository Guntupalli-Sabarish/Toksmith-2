import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.input_service.input_layer import InputService
from app.models.input import InputSource

async def main():
    print("Initializing InputService...")
    try:
        service = InputService()
        
        # Test with a script input
        print("Testing with sample input...")
        result = service.create_content_from_script("This is a test script.")
        
        if result and result.content == "This is a test script.":
            print("[SUCCESS] Success")
        else:
            print("[FAILED] Failed: Content mismatch")
            
    except Exception as e:
        print(f"[FAILED] Failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
