"""
FastAPI dependencies for dependency injection.
"""

from functools import lru_cache
from backend.clients.gemini_client import GeminiClient
from backend.core.generator import AssignmentGenerator
from backend.config import get_settings


@lru_cache()
def get_gemini_client() -> GeminiClient:
    """
    Get Gemini client instance (cached).

    Returns:
        GeminiClient instance
    """
    settings = get_settings()
    return GeminiClient(api_key=settings.gemini_api_key)


def get_generator() -> AssignmentGenerator:
    """
    Get assignment generator instance.

    Returns:
        AssignmentGenerator instance
    """
    client = get_gemini_client()
    return AssignmentGenerator(gemini_client=client)
