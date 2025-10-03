import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Config module loaded (initialization deferred)")

class Config:
    # Frontend Origin - support both FRONTEND_URL and FRONTEND_ORIGIN for compatibility
    # Load environment variables when the class is first accessed
    _frontend_origin = None
    
    @classmethod
    @property
    def FRONTEND_ORIGIN(cls):
        if cls._frontend_origin is None:
            from dotenv import load_dotenv
            logger.info("Loading dotenv in Config...")
            load_dotenv()
            logger.info("Dotenv loaded in Config")
            cls._frontend_origin = os.getenv("FRONTEND_URL") or os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
            logger.info(f"Config.FRONTEND_ORIGIN set to: {cls._frontend_origin}")
        return cls._frontend_origin