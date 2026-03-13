"""Common validation and sanitization utilities."""

import re
from datetime import date, datetime
from typing import Optional, Any, Dict, List, Union
import html


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


def sanitize_string(
    value: str, 
    max_length: Optional[int] = None,
    allow_html: bool = False,
    strip_whitespace: bool = True
) -> str:
    """
    Comprehensive string sanitization for XSS prevention.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length (truncates if exceeded)
        allow_html: If False, strips all HTML tags and escapes HTML entities
        strip_whitespace: If True, removes leading/trailing whitespace
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove leading/trailing whitespace
    if strip_whitespace:
        sanitized = value.strip()
    else:
        sanitized = value
    
    # Remove HTML tags and escape HTML entities if HTML is not allowed
    if not allow_html:
        # Escape HTML entities to prevent XSS
        sanitized = html.escape(sanitized, quote=True)
        # Remove any HTML tags using regex (basic HTML tag removal)
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Remove control characters (except newline, tab, carriage return)
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """
    Sanitize file names to prevent path traversal and injection attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename safe for filesystem use
    """
    if not isinstance(filename, str):
        filename = str(filename)
    
    # Remove path components
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Remove leading dots and spaces
    filename = filename.lstrip('. ')
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1F\x7F]', '', filename)
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Limit length (typical filesystem limit)
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255 - len(ext) - 1] + ('.' + ext if ext else '')
    
    return filename.strip()


def sanitize_sql_like_pattern(pattern: str) -> str:
    """
    Sanitize string for use in SQL LIKE patterns.
    Escapes special characters that could be used for SQL injection.
    
    Args:
        pattern: String pattern to sanitize
    
    Returns:
        Sanitized pattern safe for SQL LIKE queries
    """
    if not isinstance(pattern, str):
        pattern = str(pattern)
    
    # Escape SQL LIKE special characters: %, _, \
    sanitized = pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    
    return sanitized


def sanitize_url(url: str) -> str:
    """
    Sanitize URL to prevent javascript: and data: protocol attacks.
    
    Args:
        url: URL string to sanitize
    
    Returns:
        Sanitized URL or empty string if invalid
    """
    if not isinstance(url, str):
        url = str(url)
    
    url = url.strip().lower()
    
    # Block dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:']
    for protocol in dangerous_protocols:
        if url.startswith(protocol):
            return ''
    
    # Only allow http, https, mailto, tel
    allowed_protocols = ['http://', 'https://', 'mailto:', 'tel:']
    if not any(url.startswith(protocol) for protocol in allowed_protocols):
        # If no protocol, assume it's not a full URL
        return sanitize_string(url)
    
    return url


def sanitize_dict(data: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
    """
    Recursively sanitize all string values in a dictionary.
    
    Args:
        data: Dictionary to sanitize
        recursive: If True, recursively sanitize nested dictionaries and lists
    
    Returns:
        Dictionary with sanitized string values
    """
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize key
        sanitized_key = sanitize_string(str(key)) if isinstance(key, str) else key
        
        # Sanitize value
        if isinstance(value, str):
            sanitized_value = sanitize_string(value)
        elif isinstance(value, dict) and recursive:
            sanitized_value = sanitize_dict(value, recursive=True)
        elif isinstance(value, list) and recursive:
            sanitized_value = sanitize_list(value, recursive=True)
        else:
            sanitized_value = value
        
        sanitized[sanitized_key] = sanitized_value
    
    return sanitized


def sanitize_list(data: List[Any], recursive: bool = True) -> List[Any]:
    """
    Recursively sanitize all string values in a list.
    
    Args:
        data: List to sanitize
        recursive: If True, recursively sanitize nested dictionaries and lists
    
    Returns:
        List with sanitized string values
    """
    sanitized = []
    
    for item in data:
        if isinstance(item, str):
            sanitized.append(sanitize_string(item))
        elif isinstance(item, dict) and recursive:
            sanitized.append(sanitize_dict(item, recursive=True))
        elif isinstance(item, list) and recursive:
            sanitized.append(sanitize_list(item, recursive=True))
        else:
            sanitized.append(item)
    
    return sanitized


def sanitize_request_data(data: Union[Dict, List, str, Any]) -> Union[Dict, List, str, Any]:
    """
    Sanitize request data (handles dict, list, or string).
    
    Args:
        data: Request data to sanitize
    
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return sanitize_dict(data, recursive=True)
    elif isinstance(data, list):
        return sanitize_list(data, recursive=True)
    elif isinstance(data, str):
        return sanitize_string(data)
    else:
        return data

