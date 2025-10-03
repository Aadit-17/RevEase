import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv
import logging

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting database module initialization...")
logger.info("Loading dotenv...")
load_dotenv()
logger.info("Dotenv loaded")

# Supabase configuration
logger.info("Checking Supabase environment variables...")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

logger.info(f"SUPABASE_URL present: {bool(SUPABASE_URL)}")
logger.info(f"SUPABASE_KEY present: {bool(SUPABASE_KEY)}")

# Mask the values for logging
masked_url = SUPABASE_URL[:20] + "..." if SUPABASE_URL else ""
masked_key = SUPABASE_KEY[:10] + "..." if SUPABASE_KEY else ""
logger.info(f"SUPABASE_URL (masked): {masked_url}")
logger.info(f"SUPABASE_KEY (masked): {masked_key}")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    logger.info("get_supabase_client called")
    
    # Validate configuration
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL not set in environment variables!")
        raise ValueError("SUPABASE_URL environment variable is required")
    
    if not SUPABASE_KEY:
        logger.error("SUPABASE_KEY not set in environment variables!")
        raise ValueError("SUPABASE_KEY environment variable is required")
    
    try:
        logger.info(f"Creating Supabase client for URL: {masked_url}...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client created successfully")
        
        # Test the connection with a simple query
        logger.info("Testing Supabase connection...")
        result = supabase.table("reviews").select("id").limit(1).execute()
        logger.info(f"Connection test successful, got {len(result.data) if result.data else 0} rows")
        
        return supabase
    except Exception as e:
        logger.error(f"Failed to create or test Supabase client: {str(e)}", exc_info=True)
        raise Exception(f"Failed to connect to Supabase database: {str(e)}")