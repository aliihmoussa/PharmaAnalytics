"""Process STORE Excel file and insert into inventory_stock."""

import logging
from pathlib import Path
from datetime import datetime, date
from typing import Tuple

import polars as pl

from backend.app.database.models import InventoryStock
from backend.app.database.session import get_db_session
from backend.app.modules.ingestion.ingestion import IngestionLoader
from backend.app.modules.ingestion.transformation import standardize_date
from backend.app.modules.inventory.schema import INVENTORY_FIELD_MAPPINGS, STORE_DATA_SHEET

logger = logging.getLogger(__name__)


def _safe_int(val, default=None):
    if val is None:
        return default
    if isinstance(val, float) and (val != val or val == float('inf')):
        return default
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=None):
    if val is None:
        return default
    if isinstance(val, float) and (val != val or val == float('inf')):
        return default
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return default


def _parse_date_val(val):
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    # Polars Date may appear as date/datetime after to_dicts()
    if hasattr(val, 'date') and callable(val.date):
        return val.date()
    s = standardize_date(val)
    if not s:
        return None
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError:
        return None


def process_store_file(file_path: Path, file_name: str, sheet_name: str = None) -> Tuple[int, int]:
    """
    Load STORE Excel (data sheet), map columns, normalize, and insert into inventory_stock.

    Args:
        file_path: Path to the Excel file
        file_name: Original file name (for source_file)
        sheet_name: Sheet name (default: rep25071808450909)

    Returns:
        (successful_count, failed_count)
    """
    sheet_name = sheet_name or STORE_DATA_SHEET
    loader = IngestionLoader()
    logger.info(f"Loading STORE Excel sheet={sheet_name} from {file_path}")
    df = loader.load_excel_file(file_path, sheet_name=sheet_name)

    if df.is_empty():
        raise ValueError("STORE file is empty")

    # Map columns to canonical names
    rename = {}
    for src, canonical in INVENTORY_FIELD_MAPPINGS.items():
        if src in df.columns:
            rename[src] = canonical
    if not rename:
        raise ValueError(f"No STORE columns found. Expected one of {list(INVENTORY_FIELD_MAPPINGS.keys())}")
    df = df.rename(rename)

    # Add source_file
    df = df.with_columns(pl.lit(file_name).alias('source_file'))

    # Required columns for insert
    required = ['doc_id', 'transaction_date', 'movement_number', 'drug_code', 'drug_name', 'quantity', 'unit_price', 'total_price']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column after mapping: {col}")

    # Normalize drug_code (uppercase, strip)
    if 'drug_code' in df.columns:
        df = df.with_columns(pl.col('drug_code').str.strip_chars().str.to_uppercase().alias('drug_code'))
    if 'drug_name' in df.columns:
        df = df.with_columns(pl.col('drug_name').str.strip_chars().alias('drug_name'))

    # Drop rows missing required fields
    df = df.filter(
        pl.col('doc_id').is_not_null() & pl.col('transaction_date').is_not_null() &
        pl.col('movement_number').is_not_null() & pl.col('drug_code').is_not_null() &
        pl.col('quantity').is_not_null()
    )

    records = df.to_dicts()
    session = get_db_session()
    successful = 0
    failed = 0

    try:
        for r in records:
            try:
                tdate = r.get('transaction_date')
                if isinstance(tdate, str):
                    tdate = _parse_date_val(tdate)
                elif hasattr(tdate, 'date'):
                    tdate = tdate.date() if callable(getattr(tdate, 'date', None)) else tdate

                if tdate is None:
                    failed += 1
                    continue

                doc_id = _safe_int(r.get('doc_id'), 0)
                movement_number = _safe_int(r.get('movement_number'))
                if movement_number is None:
                    failed += 1
                    continue

                quantity = _safe_int(r.get('quantity'))
                if quantity is None:
                    failed += 1
                    continue

                unit_price = _safe_float(r.get('unit_price'), 0.0)
                total_price = _safe_float(r.get('total_price'), 0.0)

                row = InventoryStock(
                    doc_id=doc_id,
                    line_number=_safe_int(r.get('line_number')),
                    cat=_safe_int(r.get('cat')),
                    cr=_safe_int(r.get('cr')),
                    transaction_date=tdate,
                    movement_number=movement_number,
                    movement_description=str(r.get('movement_description')).strip() if r.get('movement_description') else None,
                    drug_code=(r.get('drug_code') or '').strip().upper(),
                    drug_name=(r.get('drug_name') or '').strip()[:255],
                    m_field=str(r.get('m_field')).strip()[:50] if r.get('m_field') else None,
                    cs=_safe_int(r.get('cs')),
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    voucher=str(r.get('voucher')).strip()[:50] if r.get('voucher') else None,
                    source_file=r.get('source_file'),
                )
                session.add(row)
                successful += 1
            except Exception as e:
                logger.warning(f"Skip row: {e}")
                failed += 1

        session.commit()
        logger.info(f"Inventory ingestion: {successful} successful, {failed} failed")
        return successful, failed
    except Exception as e:
        session.rollback()
        logger.error(f"Inventory ingestion failed: {e}", exc_info=True)
        raise
    finally:
        session.close()
