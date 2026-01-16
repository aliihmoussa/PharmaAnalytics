"""Configuration management for Flask application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator


class Config(BaseSettings):
    """Application configuration."""
    
    # Flask Configuration
    FLASK_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Database Configuration
    DB_USER: str = os.getenv("DB_USER", "pharma_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "pharma_password")
    DB_NAME: str = os.getenv("DB_NAME", "pharma_analytics_db")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    @model_validator(mode='after')
    def construct_database_url(self):
        """Construct DATABASE_URL if not provided, or parse it to extract components."""
        if self.DATABASE_URL:
            # Parse DATABASE_URL to extract components for SQLAlchemy
            # Format: postgresql://user:password@host:port/database
            try:
                from urllib.parse import urlparse
                parsed = urlparse(self.DATABASE_URL)
                if parsed.username:
                    self.DB_USER = parsed.username
                if parsed.password:
                    self.DB_PASSWORD = parsed.password
                if parsed.hostname:
                    self.DB_HOST = parsed.hostname
                if parsed.port:
                    self.DB_PORT = parsed.port
                if parsed.path:
                    self.DB_NAME = parsed.path.lstrip('/')
            except Exception:
                # If parsing fails, keep defaults
                pass
        else:
            # Construct DATABASE_URL from components
            self.DATABASE_URL = (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse DEBUG from string if needed."""
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    # Redis Configuration - Used ONLY for Celery broker and result backend
    # Redis is NOT used as a database, only for Celery task queue
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Celery Configuration - Uses Redis as broker and result backend
    # All application data is stored in PostgreSQL
    CELERY_BROKER_URL: Optional[str] = os.getenv(
        "CELERY_BROKER_URL",
        f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}"
    )
    CELERY_RESULT_BACKEND: Optional[str] = os.getenv(
        "CELERY_RESULT_BACKEND",
        f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}"
    )
    
    # File Path Configuration for Direct Ingestion
    ALLOWED_INGESTION_PATHS: str = os.getenv(
        "ALLOWED_INGESTION_PATHS",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()

