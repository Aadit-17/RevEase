import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Create Supabase client (will be created when first accessed)
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client instance - lazy initialization"""
    global supabase
    
    # Return cached client if available
    if supabase is not None:
        return supabase
    
    # Validate configuration
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase