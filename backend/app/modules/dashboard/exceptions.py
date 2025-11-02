"""Analytics feature-specific exceptions."""

from backend.app.shared.exceptions import AppException, NotFoundError


class AnalyticsException(AppException):
    """Base analytics exception."""
    pass


class NoDataFoundException(NotFoundError):
    """No data found for specified filters."""
    pass


class InvalidChartTypeException(AnalyticsException):
    """Invalid chart type requested."""
    
    def __init__(self, chart_type: str):
        super().__init__(
            message=f"Invalid chart type: {chart_type}",
            code="INVALID_CHART_TYPE",
            status_code=400
        )

