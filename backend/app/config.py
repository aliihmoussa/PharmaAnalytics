"""Configuration management for Flask application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator


class Config(BaseSettings):
    """Application configuration.

    All fields use plain defaults so pydantic-settings loads from .env at
    instantiation time. Do not use os.getenv() in defaults (evaluated at
    class definition time, before .env is loaded).
    """

    # Flask Configuration
    FLASK_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Database Configuration (plain defaults; loaded from .env by BaseSettings)
    DB_USER: str = "pharma_user"
    DB_PASSWORD: str = "pharma_password"
    DB_NAME: str = "pharma_analytics_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

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

        # Construct Celery URLs from REDIS_* if not set
        redis_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = redis_url
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = redis_url

        return self
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse DEBUG from string if needed."""
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"

    # Redis Configuration - Used ONLY for Celery broker and result backend
    # Redis is NOT used as a database, only for Celery task queue
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery Configuration - Uses Redis as broker and result backend
    # All application data is stored in PostgreSQL
    # If not set in env/.env, constructed from REDIS_* in validator below
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # File Path Configuration for Direct Ingestion
    ALLOWED_INGESTION_PATHS: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()

