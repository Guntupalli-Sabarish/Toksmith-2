"""
Simple script to run the server and show output
"""
import uvicorn
from src.main import app

if __name__ == "__main__":
    print("="*60)
    print("Starting ToksMith Input Layer...")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

