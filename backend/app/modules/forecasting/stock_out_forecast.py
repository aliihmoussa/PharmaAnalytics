"""Stock-out forecast: combine inventory_stock with demand forecast to predict when stock runs out."""

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func

from backend.app.database.models import InventoryStock
from backend.app.database.session import get_db_session
from backend.app.modules.forecasting.forecast_service import ForecastService

logger = logging.getLogger(__name__)

# Threshold (days) below which we flag as at_risk
AT_RISK_DAYS_THRESHOLD = 7


def get_current_stock(drug_code: str, as_of_date: Optional[date] = None) -> Optional[int]:
    """
    Sum quantity from inventory_stock for a drug (all movements up to as_of_date).
    Returns None if no rows.
    """
    as_of_date = as_of_date or date.today()
    session = get_db_session()
    try:
        row = session.query(func.sum(InventoryStock.quantity)).filter(
            InventoryStock.drug_code == drug_code,
            InventoryStock.transaction_date <= as_of_date,
        ).scalar()
        return int(row) if row is not None else None
    finally:
        session.close()


def get_drug_name_from_inventory(drug_code: str) -> Optional[str]:
    """Get drug_name from inventory_stock (any row)."""
    session = get_db_session()
    try:
        row = session.query(InventoryStock.drug_name).filter(
            InventoryStock.drug_code == drug_code,
        ).first()
        return row[0] if row else None
    finally:
        session.close()


def get_forecasted_daily_demand(drug_code: str, forecast_days: int = 30) -> Optional[float]:
    """
    Call existing XGBoost demand forecast for drug_code and return average daily predicted demand.
    Returns None if forecast fails or has no data.
    """
    try:
        service = ForecastService()
        result = service.forecast(drug_code=drug_code, forecast_days=forecast_days, test_size=30)
        forecast_list = result.get('forecast') or []
        if not forecast_list:
            return None
        preds = [float(item.get('predicted', 0) or 0) for item in forecast_list]
        if not preds:
            return None
        avg = sum(preds) / len(preds)
        return avg if avg > 0 else None
    except Exception as e:
        logger.warning(f"Demand forecast failed for {drug_code}: {e}")
        return None


def compute_stock_out_forecast(
    drug_code: str,
    drug_name: Optional[str] = None,
    as_of_date: Optional[date] = None,
    forecast_days: int = 30,
) -> Dict:
    """
    Compute stock-out forecast for one drug: current stock, forecasted daily demand,
    forecasted days until stock-out, and optional forecasted stock-out date.

    Returns dict with keys: drug_code, drug_name, current_stock, forecasted_daily_demand,
    forecasted_days_until_stockout, forecasted_stockout_date, at_risk.
    """
    as_of_date = as_of_date or date.today()
    if drug_name is None:
        drug_name = get_drug_name_from_inventory(drug_code) or drug_code
    out = {
        'drug_code': drug_code,
        'drug_name': drug_name,
        'current_stock': None,
        'forecasted_daily_demand': None,
        'forecasted_days_until_stockout': None,
        'forecasted_stockout_date': None,
        'at_risk': False,
    }

    current_stock = get_current_stock(drug_code, as_of_date)
    out['current_stock'] = current_stock

    if current_stock is None:
        return out

    daily_demand = get_forecasted_daily_demand(drug_code, forecast_days=forecast_days)
    out['forecasted_daily_demand'] = round(daily_demand, 2) if daily_demand is not None else None

    if daily_demand is None or daily_demand <= 0:
        return out

    days_until = current_stock / daily_demand
    out['forecasted_days_until_stockout'] = round(days_until, 1)
    out['forecasted_stockout_date'] = (as_of_date + timedelta(days=days_until)).isoformat()
    out['at_risk'] = days_until < AT_RISK_DAYS_THRESHOLD

    return out


def get_drug_codes_with_inventory(limit: Optional[int] = None) -> List[str]:
    """Return list of drug_codes that have at least one row in inventory_stock."""
    session = get_db_session()
    try:
        q = session.query(InventoryStock.drug_code).distinct()
        if limit:
            q = q.limit(limit)
        return [r[0] for r in q.all()]
    finally:
        session.close()


def get_top_at_risk_drugs(limit: int = 20, as_of_date: Optional[date] = None) -> List[Dict]:
    """
    For each drug in inventory_stock, compute stock-out forecast; sort by lowest
    forecasted_days_until_stockout and return top `limit`. Drugs with no demand forecast
    or infinite days are sorted last.
    """
    as_of_date = as_of_date or date.today()
    drug_codes = get_drug_codes_with_inventory()
    results = []
    for code in drug_codes:
        try:
            row = compute_stock_out_forecast(code, as_of_date=as_of_date)
            results.append(row)
        except Exception as e:
            logger.warning(f"Stock-out forecast failed for {code}: {e}")

    # Sort: lowest days first (None/inf last)
    def sort_key(r):
        d = r.get('forecasted_days_until_stockout')
        if d is None:
            return float('inf')
        return d

    results.sort(key=sort_key)
    return results[:limit]
