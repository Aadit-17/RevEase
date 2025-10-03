import uvicorn
import os
import logging
from dotenv import load_dotenv

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting start.py script...")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {os.environ.get('PYTHONPATH', 'Not set')}")

# Load environment variables
logger.info("Loading dotenv...")
load_dotenv()
logger.info("Dotenv loaded")

def check_env_vars():
    """Check if required environment variables are set"""
    logger.info("Checking environment variables...")
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    logger.info(f"Required vars: {required_vars}")
    logger.info(f"Missing vars: {missing_vars}")
    
    if missing_vars:
        # Log warning but don't fail - runtime environment might have these
        logger.warning(f"WARNING: {', '.join(missing_vars)} not set in environment variables!")
        logger.warning("Please set these values in your deployment environment variables for the application to work properly.")
        return False
    return True

if __name__ == "__main__":
    logger.info("Main block started")
    
    # Check environment variables
    env_ok = check_env_vars()
    logger.info(f"Environment check result: {env_ok}")
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Using port: {port}")
    
    logger.info(f"Environment variables at startup:")
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['SUPABASE', 'GEMINI', 'PORT']):
            # Mask sensitive values
            if 'KEY' in key.upper() or 'SECRET' in key.upper():
                logger.info(f"  {key}: {value[:5]}...{value[-5:] if len(value) > 10 else '***'}")
            else:
                logger.info(f"  {key}: {value}")
    
    logger.info(f"Starting server on port {port}")
    
    # Run the FastAPI application
    try:
        logger.info("Calling uvicorn.run...")
        uvicorn.run("review.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise