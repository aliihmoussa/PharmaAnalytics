"""Data ingestion processor for loading files into database."""

import polars as pl
from pathlib import Path
import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime, date
import io
import csv

from backend.app.modules.ingestion.ingestion import load_file
from backend.app.modules.ingestion.transformation import calculate_age_features, extract_time_features, prepare_for_database, calculate_derived_fields
from backend.app.modules.ingestion.cleaning import create_derived_features, generate_quality_report
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session, engine
from backend.app.modules.ingestion.dal import DataUploadDAL
from backend.app.modules.ingestion.exceptions import IngestionProcessingError

logger = logging.getLogger(__name__)


class IngestionProcessor:
    """Processes file ingestion into database."""
    
    BATCH_SIZE = 10000  # Process in batches of 10k rows
    
    def __init__(self, ingestion_log_id, update_progress_callback=None):
        """
        Initialize processor.
        
        Args:
            ingestion_log_id: ID of ingestion log entry
            update_progress_callback: Optional callback to update job progress
        """
        self.ingestion_log_id = ingestion_log_id
        self.update_progress = update_progress_callback
        self.dal = DataUploadDAL()
    
    def process_file(self, file_path: Path, file_name: str) -> Tuple[int, int]:
        """
        Process a file and load it into the database.
        
        Args:
            file_path: Path to the file to process
            file_name: Original file name
        
        Returns:
            Tuple of (successful_records, failed_records)
        """
        logger.info(f"Starting ingestion of {file_name} (log_id: {self.ingestion_log_id})")
        
        try:
            # Update status to processing
            self.dal.update_ingestion_log(
                self.ingestion_log_id,
                status='processing',
                started_at=datetime.now()
            )
            
            # Load file with Polars
            logger.info(f"Loading file: {file_path}")
            df = load_file(file_path)
            total_rows = len(df)
            
            if total_rows == 0:
                raise IngestionProcessingError("File is empty")
            
            # Update total records
            self.dal.update_ingestion_log(
                self.ingestion_log_id,
                total_records=total_rows
            )
            
            if self.update_progress:
                self.update_progress(10, f"Loaded {total_rows} rows")
            
            # Generate quality report (for logging)
            quality_report = generate_quality_report(df)
            logger.info(f"Quality report: {quality_report['total_rows']} rows, "
                       f"{len(quality_report['missing_values'])} columns with missing values")
            
            # Prepare data for database
            logger.info("Transforming and preparing data...")
            # Add source file first, then prepare
            from backend.app.modules.ingestion.transformation import transform_dataframe, normalize_dataframe, calculate_derived_fields
            df = transform_dataframe(df, source_file=file_name)
            df = normalize_dataframe(df)
            df = prepare_for_database(df)
            
            # Calculate derived fields if needed
            df = calculate_derived_fields(df)

            df = create_derived_features(df)
            df = extract_time_features(df)
            df = calculate_age_features(df)
            
            if self.update_progress:
                self.update_progress(30, "Data transformation completed")
            
            # Batch insert to database
            logger.info(f"Inserting {len(df)} records into database...")
            successful, failed = self._batch_insert(df)
            
            # Update final status
            self.dal.update_ingestion_log(
                self.ingestion_log_id,
                status='completed',
                successful_records=successful,
                failed_records=failed,
                completed_at=datetime.now()
            )
            
            if self.update_progress:
                self.update_progress(100, f"Completed: {successful} successful, {failed} failed")
            
            logger.info(f"Ingestion completed: {successful} successful, {failed} failed")
            return successful, failed
        
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}", exc_info=True)
            self.dal.update_ingestion_log(
                self.ingestion_log_id,
                status='failed',
                error_message=str(e),
                completed_at=datetime.now()
            )
            raise IngestionProcessingError(f"Failed to process file: {str(e)}")
    
    def _batch_insert(self, df: pl.DataFrame) -> Tuple[int, int]:
        """
        Insert dataframe into database in batches using COPY command.
        
        Args:
            df: Prepared dataframe
        
        Returns:
            Tuple of (successful_records, failed_records)
        """
        successful = 0
        failed = 0
        
        # Convert Polars DataFrame to list of dicts for easier processing
        records = df.to_dicts()
        total_batches = (len(records) + self.BATCH_SIZE - 1) // self.BATCH_SIZE
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * self.BATCH_SIZE
            end_idx = min(start_idx + self.BATCH_SIZE, len(records))
            batch = records[start_idx:end_idx]
            
            try:
                batch_successful = self._insert_batch(batch)
                successful += batch_successful
                failed += (len(batch) - batch_successful)
                
                # Update progress
                progress = 30 + int((batch_idx + 1) / total_batches * 70)
                if self.update_progress:
                    self.update_progress(
                        progress,
                        f"Processed batch {batch_idx + 1}/{total_batches} ({successful} successful)"
                    )
                
            except Exception as e:
                logger.error(f"Error inserting batch {batch_idx + 1}: {e}")
                failed += len(batch)
                # Log errors for this batch
                for record in batch:
                    self.dal.log_ingestion_error(
                        self.ingestion_log_id,
                        error_type='insertion_error',
                        error_message=str(e),
                        raw_data=str(record)
                    )
        
        return successful, failed
    
    def _insert_batch(self, batch: list) -> int:
        """
        Insert a batch of records using PostgreSQL COPY (most efficient).
        
        Args:
            batch: List of record dictionaries
        
        Returns:
            Number of successfully inserted records
        """
        # Map column names from dataframe to database schema
        column_mapping = {
            'doc_id': 'doc_id',
            'line_number': 'line_number',
            'drug_category': 'cat',
            'consuming_dept': 'cr',
            'transaction_date': 'transaction_date',
            'movement_number': 'movement_number',
            'movement_description': 'movement_description',
            'drug_code': 'drug_code',
            'drug_name': 'drug_name',
            'm_field': 'm_field',
            'supplying_dept': 'cs',
            'quantity': 'quantity',
            'unit_price': 'unit_price',
            'total_price': 'total_price',
            'admission_date': 'ad_date',
            'room_number': 'room_number',
            'bed_number': 'bed_number',
            'patient_age': 'patient_age',
            'source_file': 'source_file',
        }
        
        # Prepare records for COPY
        db_columns = [
            'doc_id', 'line_number', 'cat', 'cr', 'transaction_date', 'movement_number',
            'movement_description', 'drug_code', 'drug_name', 'm_field', 'cs',
            'quantity', 'unit_price', 'total_price', 'ad_date', 'room_number',
            'bed_number', 'patient_age', 'source_file'
        ]
        
        # Convert batch to rows for COPY
        rows = []
        for record in batch:
            row = []
            for col in db_columns:
                value = None
                # Find matching source column
                for src_col, db_col in column_mapping.items():
                    if db_col == col and src_col in record:
                        value = record[src_col]
                        break
                    # Also check direct mapping
                    if col in record:
                        value = record[col]
                
                # Handle None and date conversion
                if value is None:
                    row.append(None)
                elif isinstance(value, datetime):
                    row.append(value.date() if hasattr(value, 'date') else value)
                elif isinstance(value, pl.Date):
                    row.append(value)
                else:
                    row.append(value)
            
            rows.append(row)
        
        # Use COPY command for bulk insert (fastest method)
        try:
            with engine.raw_connection() as conn:
                cursor = conn.cursor()
                
                # Create StringIO buffer for COPY
                buffer = io.StringIO()
                writer = csv.writer(buffer, delimiter='\t')
                
                for row in rows:
                    # Convert row to strings, handle None
                    csv_row = []
                    for val in row:
                        if val is None:
                            csv_row.append('\\N')
                        elif isinstance(val, datetime):
                            csv_row.append(val.date().isoformat() if hasattr(val, 'date') else str(val).split()[0])
                        elif hasattr(val, 'date'):  # Python date object
                            csv_row.append(val.isoformat())
                        else:
                            csv_row.append(str(val))
                    writer.writerow(csv_row)
                
                buffer.seek(0)
                
                # Execute COPY
                cursor.copy_from(
                    buffer,
                    'drug_transactions',
                    columns=db_columns,
                    null='\\N',
                    sep='\t'
                )
                
                conn.commit()
                return len(batch)
        
        except Exception as e:
            logger.error(f"COPY insert failed, falling back to bulk insert: {e}")
            # Fallback to SQLAlchemy bulk insert
            return self._insert_batch_sqlalchemy(batch)
    
    def _insert_batch_sqlalchemy(self, batch: list) -> int:
        """Fallback: Insert batch using SQLAlchemy bulk insert."""
        session = get_db_session()
        try:
            # Prepare records
            db_records = []
            for record in batch:
                # Map and convert record
                db_record = DrugTransaction(
                    doc_id=record.get('doc_id') or record.get('DOC'),
                    line_number=record.get('line_number') or record.get('LINE'),
                    cat=record.get('cat') or record.get('drug_category') or record.get('CAT'),
                    cr=record.get('cr') or record.get('consuming_dept') or record.get('C.R'),
                    transaction_date=self._parse_date(record.get('transaction_date') or record.get('DATE')),
                    movement_number=record.get('movement_number') or record.get('MOV #'),
                    movement_description=record.get('movement_description') or record.get('MOV DES'),
                    drug_code=str(record.get('drug_code') or record.get('CODE', '')).strip().upper(),
                    drug_name=str(record.get('drug_name') or record.get('ARTICLE', '')).strip(),
                    m_field=record.get('m_field') or record.get('M'),
                    cs=record.get('cs') or record.get('supplying_dept') or record.get('C.S'),
                    quantity=int(record.get('quantity') or record.get('QTY', 0)),
                    unit_price=float(record.get('unit_price') or record.get('U.P', 0)),
                    total_price=float(record.get('total_price') or record.get('T.P', 0)),
                    ad_date=self._parse_date(record.get('admission_date') or record.get('AD DATE')),
                    room_number=record.get('room_number') or record.get('R'),
                    bed_number=record.get('bed_number') or record.get('U'),
                    patient_age=record.get('patient_age') or record.get('AGE'),
                    source_file=record.get('source_file'),
                )
                db_records.append(db_record)
            
            session.bulk_save_objects(db_records)
            session.commit()
            return len(batch)
        
        except Exception as e:
            session.rollback()
            logger.error(f"Bulk insert error: {e}")
            raise
        finally:
            session.close()
    
    def _parse_date(self, date_value):
        """Parse date value to date object."""
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, date):
            return date_value
        
        # Try parsing string
        try:
            return datetime.strptime(str(date_value), '%Y-%m-%d').date()
        except:
            try:
                return datetime.strptime(str(date_value), '%d/%m/%y').date()
            except:
                return None


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

