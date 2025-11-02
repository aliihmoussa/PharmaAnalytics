"""Configuration management for Flask application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration."""
    
    # Flask Configuration
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database Configuration
    DB_USER: str = os.getenv("DB_USER", "pharma_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "pharma_password")
    DB_NAME: str = os.getenv("DB_NAME", "pharma_analytics_db")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER', 'pharma_user')}:{os.getenv('DB_PASSWORD', 'pharma_password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'pharma_analytics_db')}"
    )
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()

