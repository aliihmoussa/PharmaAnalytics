"""Celery tasks for ingestion module."""

import logging
from pathlib import Path
from backend.app.extensions import celery_app
from backend.app.modules.ingestion.processors import IngestionProcessor

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='ingestion.process_file')
def process_ingestion_task(self, ingestion_log_id: str, file_path: str, file_name: str):
    """
    Celery task to process file ingestion.
    
    Args:
        ingestion_log_id: UUID string of ingestion log
        file_path: Path to the file to process
        file_name: Original file name
    
    Returns:
        Dict with successful_records and failed_records
    """
    def update_progress(progress: int, message: str = ""):
        """Update task progress."""
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': progress,
                'message': message,
                'ingestion_log_id': ingestion_log_id
            }
        )
    
    try:
        processor = IngestionProcessor(
            ingestion_log_id=ingestion_log_id,
            update_progress_callback=update_progress
        )
        
        # Process the file
        successful, failed = processor.process_file(Path(file_path), file_name)
        
        # Clean up temp file
        try:
            Path(file_path).unlink()
            logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        return {
            'successful_records': successful,
            'failed_records': failed,
            'status': 'completed'
        }
    
    except Exception as e:
        logger.error(f"Task failed for ingestion {ingestion_log_id}: {e}", exc_info=True)
        raise

