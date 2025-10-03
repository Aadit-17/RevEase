import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

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
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase