"""Common validation utilities."""

from datetime import date, datetime
from typing import Optional


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string in various formats."""
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%Y/%m/%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate that start_date is before end_date."""
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")
    return True


def sanitize_string(value: str, max_length: int = None) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        return str(value)
    
    # Remove leading/trailing whitespace
    sanitized = value.strip()
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

