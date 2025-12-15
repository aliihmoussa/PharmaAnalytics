"""Reset database tables - clears transaction data and optionally ingestion logs."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import get_db_session, engine
from backend.app.database.models import DrugTransaction, DataIngestionLog, DataIngestionError
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_transactions(confirm: bool = False):
    """Clear all drug transaction records."""
    if not confirm:
        logger.warning("This will delete ALL transaction data. Set confirm=True to proceed.")
        return
    
    session = get_db_session()
    try:
        count = session.query(DrugTransaction).count()
        logger.info(f"Found {count} transaction records")
        
        session.query(DrugTransaction).delete()
        session.commit()
        
        logger.info(f"✓ Deleted {count} transaction records from drug_transactions table")
    except Exception as e:
        session.rollback()
        logger.error(f"Error resetting transactions: {e}")
        raise
    finally:
        session.close()


def reset_ingestion_logs(confirm: bool = False):
    """Clear all ingestion logs."""
    if not confirm:
        logger.warning("This will delete ALL ingestion logs. Set confirm=True to proceed.")
        return
    
    session = get_db_session()
    try:
        count = session.query(DataIngestionLog).count()
        logger.info(f"Found {count} ingestion log entries")
        
        session.query(DataIngestionLog).delete()
        session.commit()
        
        logger.info(f"✓ Deleted {count} ingestion log entries")
    except Exception as e:
        session.rollback()
        logger.error(f"Error resetting ingestion logs: {e}")
        raise
    finally:
        session.close()


def reset_ingestion_errors(confirm: bool = False):
    """Clear all ingestion error records."""
    if not confirm:
        logger.warning("This will delete ALL ingestion errors. Set confirm=True to proceed.")
        return
    
    session = get_db_session()
    try:
        count = session.query(DataIngestionError).count()
        logger.info(f"Found {count} ingestion error records")
        
        session.query(DataIngestionError).delete()
        session.commit()
        
        logger.info(f"✓ Deleted {count} ingestion error records")
    except Exception as e:
        session.rollback()
        logger.error(f"Error resetting ingestion errors: {e}")
        raise
    finally:
        session.close()


def reset_all(confirm: bool = False, keep_logs: bool = True):
    """
    Reset all data tables.
    
    Args:
        confirm: Must be True to proceed
        keep_logs: If True, keeps ingestion logs and errors (only clears transactions)
    """
    if not confirm:
        logger.warning("This will delete data. Set confirm=True to proceed.")
        return
    
    logger.info("=" * 60)
    logger.info("RESETTING DATABASE")
    logger.info("=" * 60)
    
    # Always reset transactions
    reset_transactions(confirm=True)
    
    if not keep_logs:
        reset_ingestion_logs(confirm=True)
        reset_ingestion_errors(confirm=True)
    else:
        logger.info("Keeping ingestion logs and errors (for history)")
    
    logger.info("=" * 60)
    logger.info("RESET COMPLETE")
    logger.info("=" * 60)
    
    # Show current counts
    session = get_db_session()
    try:
        tx_count = session.query(DrugTransaction).count()
        log_count = session.query(DataIngestionLog).count()
        error_count = session.query(DataIngestionError).count()
        
        logger.info(f"\nCurrent database state:")
        logger.info(f"  Transactions: {tx_count}")
        logger.info(f"  Ingestion logs: {log_count}")
        logger.info(f"  Ingestion errors: {error_count}")
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reset database tables")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Reset all tables (transactions, logs, errors)"
    )
    parser.add_argument(
        "--transactions",
        action="store_true",
        help="Reset only transaction data"
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Reset ingestion logs"
    )
    parser.add_argument(
        "--errors",
        action="store_true",
        help="Reset ingestion errors"
    )
    parser.add_argument(
        "--keep-logs",
        action="store_true",
        default=True,
        help="Keep ingestion logs when using --all (default: True)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm deletion (required for safety)"
    )
    
    args = parser.parse_args()
    
    if not args.confirm:
        logger.error("ERROR: --confirm flag is required for safety")
        logger.info("Example: python scripts/reset_database.py --transactions --confirm")
        sys.exit(1)
    
    if args.all:
        reset_all(confirm=True, keep_logs=args.keep_logs)
    elif args.transactions:
        reset_transactions(confirm=True)
    elif args.logs:
        reset_ingestion_logs(confirm=True)
    elif args.errors:
        reset_ingestion_errors(confirm=True)
    else:
        parser.print_help()
        sys.exit(1)

