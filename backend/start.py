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
        # Log warning but don't fail - Vercel might set these at runtime
        print(f"WARNING: {', '.join(missing_vars)} not set in environment variables!")
        print("Please set these values in your Vercel environment variables for the application to work properly.")
        return False
    return True

if __name__ == "__main__":
    # Check environment variables
    check_env_vars()
    
    # Run the FastAPI application
    uvicorn.run("review.main:app", host="0.0.0.0", port=8000, reload=False)