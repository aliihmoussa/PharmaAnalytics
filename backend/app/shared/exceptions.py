"""Base exception classes for the application."""


class AppException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: str = None, status_code: int = 500):
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", status_code: int = 400):
        super().__init__(message, code, status_code)


class NotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, message: str, code: str = "NOT_FOUND", status_code: int = 404):
        super().__init__(message, code, status_code)


class DatabaseError(AppException):
    """Database operation error."""
    
    def __init__(self, message: str, code: str = "DATABASE_ERROR", status_code: int = 500):
        super().__init__(message, code, status_code)

