"""SQLAlchemy session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.app.config import config
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    config.DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before using
    echo=config.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def get_db_session():
    """Get a database session (use as context manager or call close())."""
    return SessionLocal()


def init_db():
    """Initialize database tables."""
    from backend.app.database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def close_db():
    """Close all database connections."""
    SessionLocal.remove()
    engine.dispose()
    logger.info("Database connections closed")

