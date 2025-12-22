"""
Supabase Client Configuration
Provides singleton clients for Supabase services (Auth, Database, Storage)
"""
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from loguru import logger

from app.core.config import settings


class SupabaseClient:
    """Singleton Supabase client wrapper"""
    
    _instance: Client | None = None
    _admin_instance: Client | None = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get Supabase client with anon key (for user operations)"""
        if cls._instance is None:
            if not settings.supabase_url or not settings.supabase_anon_key:
                raise ValueError("Supabase URL and Anon Key must be configured")
            
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            logger.info("Supabase client initialized")
        
        return cls._instance
    
    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key (for admin operations)"""
        if cls._admin_instance is None:
            if not settings.supabase_url or not settings.supabase_service_role_key:
                raise ValueError("Supabase URL and Service Role Key must be configured")
            
            cls._admin_instance = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            logger.info("Supabase admin client initialized")
        
        return cls._admin_instance


# Convenience functions
def get_supabase() -> Client:
    """Get the default Supabase client"""
    return SupabaseClient.get_client()


def get_supabase_admin() -> Client:
    """Get the admin Supabase client"""
    return SupabaseClient.get_admin_client()
