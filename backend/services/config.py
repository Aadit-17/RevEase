import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading config module...")
logger.info("Loading dotenv...")
load_dotenv()
logger.info("Dotenv loaded")

class Config:
    # Frontend Origin - support both FRONTEND_URL and FRONTEND_ORIGIN for compatibility
    FRONTEND_ORIGIN = os.getenv("FRONTEND_URL") or os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    logger.info(f"Config.FRONTEND_ORIGIN set to: {FRONTEND_ORIGIN}")