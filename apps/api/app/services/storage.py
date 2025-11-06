"""Supabase Storage utilities for signed URLs"""

from supabase import create_client, Client
from app.config import settings

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client


def get_signed_url(path: str, expires_in: int = 3600) -> str:
    """
    Generate a signed URL for a private storage file.
    
    Args:
        path: Storage path (e.g., "resumes/{uuid}/resume.pdf")
        expires_in: URL expiration time in seconds (default: 1 hour)
    
    Returns:
        Signed URL string
    """
    if not path:
        return ""
    
    supabase = get_supabase_client()
    
    # Remove leading slash if present
    path = path.lstrip("/")
    
    try:
        signed_url = supabase.storage.from_("resumes").create_signed_url(
            path=path,
            expires_in=expires_in,
        )
        return signed_url.get("signedURL", "")
    except Exception:
        # Fallback: return empty string if generation fails
        return ""

