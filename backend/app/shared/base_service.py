"""Base service class for all service layers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base class for all services."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _validate_input(self, data: Dict[str, Any], required_fields: list) -> None:
        """
        Validate input data.
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
            
        Raises:
            ValueError: If required fields are missing
        """
        missing = [field for field in required_fields if field not in data or data[field] is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
    
    def _format_response(self, data: Any, status: str = "success") -> Dict[str, Any]:
        """
        Format service response.
        
        Args:
            data: Response data
            status: Response status
            
        Returns:
            Formatted response dictionary
        """
        return {
            'data': data,
            'status': status
        }
    
    def _handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle and log errors.
        
        Args:
            error: Exception object
            context: Additional context information
        """
        self.logger.error(f"Error in {self.__class__.__name__}: {context} - {str(error)}", exc_info=True)
        raise

