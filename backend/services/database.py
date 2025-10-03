import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    # Validate configuration
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL not set in environment variables!")
        raise ValueError("SUPABASE_URL environment variable is required")
    
    if not SUPABASE_KEY:
        logger.error("SUPABASE_KEY not set in environment variables!")
        raise ValueError("SUPABASE_KEY environment variable is required")
    
    try:
        logger.info(f"Creating Supabase client for URL: {SUPABASE_URL[:30]}...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client created successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}", exc_info=True)
        raise Exception(f"Failed to connect to Supabase database: {str(e)}")