import uvicorn
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return False
    return True

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Run the FastAPI application
    try:
        uvicorn.run("review.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        raise