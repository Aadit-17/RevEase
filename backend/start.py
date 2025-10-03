import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        # WARNING: SUPABASE_URL and/or SUPABASE_KEY not set in environment variables!
        # Please set these values in your .env file for the application to work properly.
        return False
    return True

if __name__ == "__main__":
    # Check environment variables
    check_env_vars()
    
    # Run the FastAPI application
    uvicorn.run("review.main:app", host="0.0.0.0", port=8000, reload=True)