from supabase import create_client, Client
from typing import Optional
from config import Config

# Store configuration values, don't create client immediately
SUPABASE_URL: Optional[str] = None
SUPABASE_KEY: Optional[str] = None
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client instance - lazy initialization"""
    global SUPABASE_URL, SUPABASE_KEY, supabase
    
    # Return cached client if available
    if supabase is not None:
        return supabase
    
    # Load configuration if not already loaded
    if SUPABASE_URL is None:
        SUPABASE_URL = Config.SUPABASE_URL
    if SUPABASE_KEY is None:
        SUPABASE_KEY = Config.SUPABASE_KEY
    
    # Validate configuration
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase