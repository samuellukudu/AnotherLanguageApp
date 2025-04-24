import os
from supabase import create_client, Client
from backend.settings import settings

# Initialize Supabase client using Pydantic settings
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

def get_supabase() -> Client:
    """Dependency override to provide Supabase client"""
    return supabase
