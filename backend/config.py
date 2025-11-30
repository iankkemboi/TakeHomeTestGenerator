"""
Configuration management for the application.
"""

import os
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    gemini_api_key: str
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # API Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Configuration - allow all localhost/127.0.0.1 origins in development
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance
    """
    return Settings()
