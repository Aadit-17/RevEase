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

# Create Supabase client (will be validated when actually used)
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    global supabase
    if supabase is None:
        # Only validate configuration when actually creating the client
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("SUPABASE_URL and/or SUPABASE_KEY not set in environment variables!")
            # Return a mock client or raise an exception that can be handled gracefully
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            raise
    
    return supabase