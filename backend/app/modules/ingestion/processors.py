"""Data ingestion processor for loading files into database."""

import polars as pl
from pathlib import Path
import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime, date
import io
import csv

from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session, engine
from backend.app.modules.ingestion.dal import DataUploadDAL
from backend.app.modules.ingestion.exceptions import IngestionProcessingError

logger = logging.getLogger(__name__)


class IngestionProcessor:
    """Processes file ingestion into database."""
    
    BATCH_SIZE = 10000  # Process in batches of 10k rows
    
    def __init__(
        self,
        ingestion_log_id,
        update_progress_callback=None,
        ingestion_module=None,
        transformation_module=None,
        cleaning_module=None,
        dal=None
    ):
        """
        Initialize processor with dependency injection.
        
        Args:
            ingestion_log_id: ID of ingestion log entry
            update_progress_callback: Optional callback to update job progress
            ingestion_module: Ingestion module (default: imported module)
            transformation_module: Transformation module (default: imported module)
            cleaning_module: Cleaning module (default: imported module)
            dal: Data access layer (default: DataUploadDAL instance)
        """
        self.ingestion_log_id = ingestion_log_id
        self.update_progress = update_progress_callback
        
        # Dependency injection with defaults for backward compatibility
        if ingestion_module is None:
            from backend.app.modules.ingestion.ingestion import IngestionLoader
            ingestion_module = IngestionLoader()
        if transformation_module is None:
            from backend.app.modules.ingestion import transformation as transformation_module
        if cleaning_module is None:
            from backend.app.modules.ingestion import cleaning as cleaning_module
        
        self.ingestion = ingestion_module
        self.transformation = transformation_module
        self.cleaning = cleaning_module
        self.dal = dal if dal is not None else DataUploadDAL()
    
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
            dal = DataUploadDAL()
            with dal:
                dal.update_ingestion_log(
                self.ingestion_log_id,
                status='processing',
                started_at=datetime.now()
            )
            
            # Detect file type
            file_type = self.ingestion.detect_file_type(file_path)
            logger.info(f"Detected file type: {file_type}")
            
            # Load file based on type
            if file_type == 'excel':
                # For Excel files, process in chunks
                return self._process_excel_file(file_path, file_name)
            else:
                # For CSV/TSV files, process normally
                return self._process_csv_file(file_path, file_name)
        
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}", exc_info=True)
            dal = DataUploadDAL()
            with dal:
                dal.update_ingestion_log(
                self.ingestion_log_id,
                status='failed',
                error_message=str(e),
                completed_at=datetime.now()
            )
            raise IngestionProcessingError(f"Failed to process file: {str(e)}")
    
    def _process_csv_file(self, file_path: Path, file_name: str) -> Tuple[int, int]:
        """Process CSV/TSV file."""
        logger.info(f"Loading CSV/TSV file: {file_path}")
        df = self.ingestion.load_file(file_path)
        total_rows = len(df)
        
        if total_rows == 0:
            raise IngestionProcessingError("File is empty")
        
        # Update total records
        dal = DataUploadDAL()
        with dal:
            dal.update_ingestion_log(
            self.ingestion_log_id,
            total_records=total_rows
        )
        
        if self.update_progress:
            self.update_progress(10, f"Loaded {total_rows} rows")
        
        # Apply cleaning pipeline
        df = self._apply_cleaning_pipeline(df, is_excel=False)
        
        # Transform and prepare for database
        df = self.transformation.transform_dataframe(df, source_file=file_name)
        df = self.transformation.normalize_dataframe(df)
        df = self.transformation.prepare_for_database(df)
        df = self.transformation.calculate_derived_fields(df)
        
        if self.update_progress:
            self.update_progress(30, "Data transformation completed")
        
        # Batch insert to database
        logger.info(f"Inserting {len(df)} records into database...")
        successful, failed = self._batch_insert(df)
        
        # Update final status
        dal = DataUploadDAL()
        with dal:
            dal.update_ingestion_log(
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
    
    def _process_excel_file(self, file_path: Path, file_name: str) -> Tuple[int, int]:
        """Process Excel file in chunks."""
        logger.info(f"Processing Excel file: {file_path}")
        
        total_successful = 0
        total_failed = 0
        total_rows = 0
        chunk_count = 0
        
        try:
            # Process Excel file in chunks
            for chunk_df in self.ingestion.load_excel_chunked(file_path, chunk_size=self.BATCH_SIZE):
                chunk_count += 1
                chunk_rows = len(chunk_df)
                total_rows += chunk_rows
                
                logger.info(f"Processing chunk {chunk_count}: {chunk_rows} rows")
                
                # Update total records (approximate, will be updated as we process)
                if chunk_count == 1:
                    dal = DataUploadDAL()
                    with dal:
                        dal.update_ingestion_log(
                        self.ingestion_log_id,
                        total_records=total_rows
                    )
                
                if self.update_progress:
                    progress = 10 + int((chunk_count * 70) / max(chunk_count, 1))
                    self.update_progress(progress, f"Processing chunk {chunk_count}: {chunk_rows} rows")
                
                # Log initial chunk state
                logger.info(f"Chunk {chunk_count}: Starting with {len(chunk_df)} rows")
                logger.info(f"Chunk {chunk_count}: Original columns: {list(chunk_df.columns)}")
                
                # Log sample data to debug column issues
                if chunk_count == 1:
                    logger.info(f"First chunk sample data (first 3 rows):")
                    try:
                        sample_df = chunk_df.head(3)
                        for col in chunk_df.columns:
                            sample_values = sample_df[col].head(3).to_list()
                            null_count = chunk_df[col].null_count()
                            logger.info(f"  Column '{col}': {null_count} nulls, sample values: {sample_values}")
                    except Exception as e:
                        logger.warning(f"Could not log sample data: {e}")
                
                # Apply cleaning pipeline (includes column mapping, type coercion, validation)
                before_cleaning = len(chunk_df)
                chunk_df = self._apply_cleaning_pipeline(chunk_df, is_excel=True)
                logger.info(f"Chunk {chunk_count}: After cleaning pipeline: {len(chunk_df)} rows (removed {before_cleaning - len(chunk_df)})")
                
                # Transform and prepare for database (column mapping already done in pipeline)
                # Only normalize and calculate derived fields
                before_normalize = len(chunk_df)
                chunk_df = self.transformation.normalize_dataframe(chunk_df)
                logger.info(f"Chunk {chunk_count}: After normalize_dataframe: {len(chunk_df)} rows")
                
                before_prepare = len(chunk_df)
                chunk_df = self.transformation.prepare_for_database(chunk_df, source_file=file_name)
                logger.info(f"Chunk {chunk_count}: After prepare_for_database: {len(chunk_df)} rows (removed {before_prepare - len(chunk_df)})")
                
                chunk_df = self.transformation.calculate_derived_fields(chunk_df)
                logger.info(f"Chunk {chunk_count}: After calculate_derived_fields: {len(chunk_df)} rows, final columns: {chunk_df.columns}")
                
                # Batch insert chunk
                if len(chunk_df) > 0:
                    logger.info(f"Chunk {chunk_count}: Inserting {len(chunk_df)} records into database")
                    successful, failed = self._batch_insert(chunk_df)
                    total_successful += successful
                    total_failed += failed
                    logger.info(f"Chunk {chunk_count}: {successful} successful, {failed} failed")
                else:
                    logger.warning(f"Chunk {chunk_count} had no valid records after cleaning and transformation")
                    # Log why records were filtered
                    logger.warning(f"Chunk {chunk_count}: All records were filtered out. Check validation logs above.")
            
            # Update final total records and status
            dal = DataUploadDAL()
            with dal:
                dal.update_ingestion_log(
                self.ingestion_log_id,
                total_records=total_rows
            )
            
            # Update final status
                dal.update_ingestion_log(
                self.ingestion_log_id,
                status='completed',
                successful_records=total_successful,
                failed_records=total_failed,
                completed_at=datetime.now()
            )
            
            if self.update_progress:
                self.update_progress(100, f"Completed: {total_successful} successful, {total_failed} failed")
            
            logger.info(f"Excel ingestion completed: {total_successful} successful, {total_failed} failed")
            return total_successful, total_failed
        
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}", exc_info=True)
            # Update status with partial results
            dal = DataUploadDAL()
            with dal:
                dal.update_ingestion_log(
                self.ingestion_log_id,
                status='failed',
                successful_records=total_successful,
                failed_records=total_failed,
                error_message=str(e),
                completed_at=datetime.now()
            )
            raise
    
    def _apply_cleaning_pipeline(self, df: pl.DataFrame, is_excel: bool = False) -> pl.DataFrame:
        """
        Apply comprehensive cleaning pipeline.
        
        Pipeline order:
        1. Excel-specific cleaning (remove empty rows, strip whitespace)
        2. Transform column names (map to database schema)
        3. Data type coercion (convert types, normalize dates)
        4. Data validation (filter invalid records - CRITICAL STEP)
        5. Data consistency (auto-correct where possible)
        
        Args:
            df: Polars DataFrame
            is_excel: Whether this is from an Excel file
        
        Returns:
            Cleaned DataFrame
        """
        original_rows = len(df)
        logger.info(f"Cleaning pipeline: Starting with {original_rows} rows")
        
        # Step 1: Excel-specific cleaning (remove empty rows, strip whitespace)
        if is_excel:
            before = len(df)
            df = self.cleaning.clean_excel_dataframe(df)
            logger.info(f"Step 1 - Excel cleaning: {len(df)} rows (removed {before - len(df)} empty rows)")
        
        # Step 2: Transform column names EARLY (before type coercion)
        # This ensures we're working with correct column names
        if any(col in df.columns for col in ['DOC', 'CODE', 'ARTICLE']):
            before = len(df)
            df = self.transformation.transform_dataframe(df)
            logger.info(f"Step 2 - Column mapping: {len(df)} rows, mapped columns: {df.columns}")
        
        # Step 3: Data type coercion (convert types, normalize dates, handle special fields)
        before = len(df)
        df, coercion_stats = self.cleaning.coerce_data_types(df)
        if coercion_stats.get('errors'):
            logger.warning(f"Step 3 - Type coercion errors: {coercion_stats['errors']}")
        logger.info(f"Step 3 - Type coercion: {len(df)} rows (no filtering, only conversion)")
        
        # Step 4: Data validation (filter invalid records - THIS IS WHERE RECORDS ARE FILTERED)
        before = len(df)
        df, validation_results = self.cleaning.validate_data_integrity(df)
        removed = before - len(df)
        if removed > 0:
            logger.warning(f"Step 4 - Validation: Removed {removed} invalid records ({removed/before*100:.1f}%)")
            # Log detailed breakdown of removal reasons
            if validation_results.get('invalid_reasons'):
                reasons = validation_results['invalid_reasons']
                logger.warning(f"  Removal breakdown:")
                for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
                    logger.warning(f"    - {reason}: {count} records")
        else:
            logger.info(f"Step 4 - Validation: All {before} records passed validation")
        
        if validation_results.get('suspicious_patterns'):
            logger.info(f"  Suspicious patterns detected: {validation_results['suspicious_patterns']}")
        
        # Step 5: Data consistency checks (auto-correct where possible, no filtering)
        before = len(df)
        df, consistency_results = self.cleaning.verify_data_consistency(df)
        if consistency_results.get('price_mismatches_corrected', 0) > 0:
            logger.info(f"Step 5 - Consistency: Corrected {consistency_results['price_mismatches_corrected']} price mismatches")
        if consistency_results.get('age_normalizations', 0) > 0:
            logger.info(f"Step 5 - Consistency: Normalized {consistency_results['age_normalizations']} age values")
        if consistency_results.get('errors'):
            logger.warning(f"Step 5 - Consistency errors: {consistency_results['errors']}")
        logger.info(f"Step 5 - Consistency: {len(df)} rows (no filtering, only corrections)")
        
        # Final summary
        total_removed = original_rows - len(df)
        if total_removed > 0:
            logger.warning(f"Cleaning pipeline summary: {len(df)}/{original_rows} records preserved ({len(df)/original_rows*100:.1f}%)")
        else:
            logger.info(f"Cleaning pipeline summary: All {original_rows} records preserved")
        
        return df
    
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
        # Note: Polars Date objects are automatically converted to Python date objects by to_dicts()
        records = df.to_dicts()
        
        # Log sample date_of_birth values to debug
        if records and 'date_of_birth' in records[0]:
            sample_dobs = [r.get('date_of_birth') for r in records[:5]]
            logger.info(f"Sample date_of_birth values from records: {sample_dobs} (types: {[type(d).__name__ for d in sample_dobs]})")
        
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
                dal = DataUploadDAL()
                with dal:
                for record in batch:
                        dal.log_ingestion_error(
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
            'date_of_birth': 'date_of_birth',
            'source_file': 'source_file',
        }
        
        # Prepare records for COPY
        db_columns = [
            'doc_id', 'line_number', 'cat', 'cr', 'transaction_date', 'movement_number',
            'movement_description', 'drug_code', 'drug_name', 'm_field', 'cs',
            'quantity', 'unit_price', 'total_price', 'ad_date', 'room_number',
                    'bed_number', 'date_of_birth', 'source_file'
        ]
        
        # Convert batch to rows for COPY
        rows = []
        skipped_count = 0
        for record in batch:
            # Validate required fields before processing
            movement_number = None
            for src_col, db_col in column_mapping.items():
                if db_col == 'movement_number' and src_col in record:
                    movement_number = record[src_col]
                    break
            # Also check direct mapping
            if movement_number is None and 'movement_number' in record:
                movement_number = record['movement_number']
            # Also check original column names
            if movement_number is None:
                movement_number = record.get('MOV #') or record.get('MOV#')
            
            # Skip records with null movement_number (required field)
            if movement_number is None:
                skipped_count += 1
                dal = DataUploadDAL()
                with dal:
                    dal.log_ingestion_error(
                    self.ingestion_log_id,
                    error_type='validation_error',
                    error_message='movement_number is required but was null',
                    raw_data=str(record)
                )
                continue
            
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
                
                # Special handling for bed_number - convert Arabic letters to English or preserve numbers
                if col == 'bed_number' and value is not None:
                    bed_str = str(value).strip()
                    # Convert Arabic letters to English
                    arabic_to_english = {'أ': 'A', 'ا': 'A', 'ب': 'B'}
                    converted = False
                    for arabic, english in arabic_to_english.items():
                        if arabic in bed_str:
                            value = english
                            converted = True
                            break
                    if not converted:
                        # If already A/B, keep it uppercase
                        if bed_str.upper() in ['A', 'B']:
                            value = bed_str.upper()
                        else:
                            # It's a number - keep as string
                            try:
                                value = str(int(float(bed_str)))  # Handle "108.0" type values
                            except (ValueError, TypeError):
                                value = bed_str  # Keep original if not numeric
                
                # Special handling for doc_id - ensure it's an integer
                if col == 'doc_id' and value is not None:
                    try:
                        value = int(float(str(value)))  # Handle "15979.0" type values
                    except (ValueError, TypeError):
                        # If conversion fails, try to extract numeric part
                        import re
                        match = re.search(r'\d+', str(value))
                        if match:
                            value = int(match.group())
                        else:
                            # If no number found, this is an error - doc_id must be numeric
                            logger.warning(f"doc_id value '{value}' cannot be converted to integer")
                            value = None
                
                # Handle None and date conversion
                if value is None:
                    row.append(None)
                elif col in ['transaction_date', 'ad_date', 'date_of_birth']:
                    # Parse date fields properly - handle various date types
                    if isinstance(value, datetime):
                        row.append(value.date() if hasattr(value, 'date') else value)
                    elif isinstance(value, date):
                        row.append(value)
                    elif isinstance(value, pl.Date):
                        # Convert Polars Date to Python date
                        try:
                            # Polars Date can be converted to Python date
                            row.append(date(value.year, value.month, value.day))
                        except (AttributeError, ValueError):
                            # Fallback: try to parse as string
                            parsed_date = self._parse_date(str(value))
                            row.append(parsed_date)
                    else:
                        # Try to parse string date or other formats
                        parsed_date = self._parse_date(value)
                        row.append(parsed_date)
                elif isinstance(value, datetime):
                    row.append(value.date() if hasattr(value, 'date') else value)
                elif isinstance(value, date):
                    row.append(value)
                elif isinstance(value, pl.Date):
                    # Convert Polars Date to Python date
                    try:
                        row.append(date(value.year, value.month, value.day))
                    except (AttributeError, ValueError):
                        row.append(value)
                else:
                    row.append(value)
            
            rows.append(row)
        
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} records with null movement_number")
        
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
                # Extract and normalize doc_id (handle both string and integer)
                doc_id_value = record.get('doc_id') or record.get('DOC')
                if doc_id_value is not None:
                    try:
                        # Try to convert to int if it's numeric
                        doc_id_value = int(float(str(doc_id_value)))
                    except (ValueError, TypeError):
                        # If not numeric, keep as string
                        doc_id_value = str(doc_id_value).strip()
                
                # Extract and normalize bed_number (handle Arabic letters and numbers)
                bed_number_value = record.get('bed_number') or record.get('U')
                if bed_number_value is not None:
                    bed_str = str(bed_number_value).strip()
                    # Convert Arabic letters to English
                    arabic_to_english = {'أ': 'A', 'ا': 'A', 'ب': 'B'}
                    for arabic, english in arabic_to_english.items():
                        if arabic in bed_str:
                            bed_number_value = english
                            break
                    else:
                        # If no Arabic letter found, check if it's A/B or a number
                        if bed_str.upper() in ['A', 'B']:
                            bed_number_value = bed_str.upper()
                        else:
                            # It's a number - keep as string (bed_number is String in DB)
                            try:
                                bed_number_value = str(int(float(bed_str)))  # Handle "108.0" type values
                            except (ValueError, TypeError):
                                bed_number_value = bed_str  # Keep original if not numeric
                
                db_record = DrugTransaction(
                    doc_id=doc_id_value,
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
                    bed_number=bed_number_value,
                    date_of_birth=self._parse_date(record.get('date_of_birth') or record.get('AGE')),
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
        """Parse date value to date object using standardize_date."""
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, date):
            return date_value
        
        # Use standardize_date for robust parsing
        from backend.app.modules.ingestion.transformation import standardize_date
        standardized = standardize_date(date_value)
        if standardized:
            try:
                return datetime.strptime(standardized, '%Y-%m-%d').date()
            except ValueError:
                return None
        return None


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

