"""Dashboard-ready data serialization."""

from typing import Dict, List, Any
import json
from datetime import date, datetime


def format_for_dashboard(data: Any, chart_type: str = 'table') -> Dict:
    """
    Format data for frontend dashboard consumption.
    
    Args:
        data: Raw data (list, dict, etc.)
        chart_type: Type of chart (table, line, bar, heatmap)
    
    Returns:
        Dictionary formatted for dashboard
    """
    if isinstance(data, list):
        # Convert list of dicts to dashboard format
        formatted = {
            'data': data,
            'count': len(data),
            'chart_type': chart_type
        }
    elif isinstance(data, dict):
        formatted = {
            'data': data,
            'chart_type': chart_type
        }
    else:
        formatted = {
            'data': data,
            'chart_type': chart_type
        }
    
    return formatted


def serialize_datetime(obj: Any) -> Any:
    """JSON serializer for datetime objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def to_json(data: Dict) -> str:
    """Convert data to JSON string."""
    return json.dumps(data, default=serialize_datetime, indent=2)

