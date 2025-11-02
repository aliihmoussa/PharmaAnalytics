"""Database initialization script."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.config import config
from backend.app.database.connection import DatabaseConnection
from backend.app.database.session import init_db
from backend.app.database.models import Base
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create database tables using SQLAlchemy models."""
    
    # Use SQLAlchemy to create tables from models
    from backend.app.database.session import engine
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created from SQLAlchemy models")
    
    # Add additional indexes and constraints using raw SQL if needed
    DatabaseConnection.initialize_pool()
    conn = DatabaseConnection.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # Composite indexes for common query patterns
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date_dept 
                ON drug_transactions(transaction_date, cr)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_drug_date 
                ON drug_transactions(drug_code, transaction_date)
            """)
            
            # Add file_hash column if not exists (for migration)
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'data_ingestion_log' 
                        AND column_name = 'file_hash'
                    ) THEN
                        ALTER TABLE data_ingestion_log 
                        ADD COLUMN file_hash VARCHAR(64);
                    END IF;
                END $$;
            """)
            
            conn.commit()
            logger.info("Additional indexes and columns created successfully")
    
    except Exception as e:
        conn.rollback()
        logger.warning(f"Error creating additional indexes (may already exist): {e}")
    finally:
        DatabaseConnection.return_connection(conn)


if __name__ == '__main__':
    logger.info("Starting database setup...")
    create_tables()
    logger.info("Database setup completed")

