"""Add database indexes for ML module performance optimization."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.app.database.connection import DatabaseConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_indexes():
    """Add performance indexes for ML queries."""
    conn = DatabaseConnection.get_connection()
    
    try:
        with conn.begin():
            # Indexes for drug_code + date queries (most common)
            logger.info("Adding indexes for ML queries...")
            
            # Composite index for drug_code + transaction_date (already exists, but ensure it)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ml_drug_date 
                ON drug_transactions(drug_code, transaction_date)
                WHERE quantity < 0
            """))
            
            # Index for department + date queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ml_dept_date 
                ON drug_transactions(cr, transaction_date)
                WHERE quantity < 0 AND cr IS NOT NULL
            """))
            
            # Index for drug_code + department + date (for department-specific profiling)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ml_drug_dept_date 
                ON drug_transactions(drug_code, cr, transaction_date)
                WHERE quantity < 0 AND cr IS NOT NULL
            """))
            
            # Index for category queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ml_category_date 
                ON drug_transactions(cat, transaction_date)
                WHERE quantity < 0 AND cat IS NOT NULL
            """))
            
            # Index for date range queries (covering index)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ml_date_covering 
                ON drug_transactions(transaction_date, drug_code, quantity, cr, cat)
                WHERE quantity < 0
            """))
            
            logger.info("Indexes created successfully")
            
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise
    finally:
        conn.close()


def create_materialized_view():
    """Create materialized view for daily aggregations (performance optimization)."""
    conn = DatabaseConnection.get_connection()
    
    try:
        with conn.begin():
            logger.info("Creating materialized view for daily aggregations...")
            
            # Drop if exists
            conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS mv_daily_drug_demand"))
            
            # Create materialized view
            conn.execute(text("""
                CREATE MATERIALIZED VIEW mv_daily_drug_demand AS
                SELECT 
                    drug_code,
                    DATE(transaction_date) as date,
                    cr as department,
                    SUM(ABS(quantity)) as daily_demand,
                    COUNT(*) as transaction_count,
                    AVG(unit_price) as avg_unit_price,
                    SUM(total_price) as total_value
                FROM drug_transactions
                WHERE quantity < 0
                GROUP BY drug_code, DATE(transaction_date), cr
            """))
            
            # Create index on materialized view
            conn.execute(text("""
                CREATE UNIQUE INDEX idx_mv_daily_drug_demand_unique 
                ON mv_daily_drug_demand(drug_code, date, department)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_mv_daily_drug_demand_date 
                ON mv_daily_drug_demand(drug_code, date)
            """))
            
            logger.info("Materialized view created successfully")
            
    except Exception as e:
        logger.error(f"Error creating materialized view: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    logger.info("Starting database optimization...")
    
    try:
        # Add indexes
        add_indexes()
        
        # Create materialized view
        create_materialized_view()
        
        logger.info("Database optimization completed successfully")
        print("\n✅ Database indexes and materialized views created successfully!")
        print("\nNote: Refresh materialized view periodically with:")
        print("   REFRESH MATERIALIZED VIEW mv_daily_drug_demand;")
        
    except Exception as e:
        logger.error(f"Failed to optimize database: {str(e)}")
        sys.exit(1)

