import uvicorn
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        # Log warning but don't fail - runtime environment might have these
        logger.warning(f"WARNING: {', '.join(missing_vars)} not set in environment variables!")
        logger.warning("Please set these values in your deployment environment variables for the application to work properly.")
        return False
    return True

if __name__ == "__main__":
    # Check environment variables
    check_env_vars()
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting server on port {port}")
    
    # Run the FastAPI application
    try:
        uvicorn.run("review.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise