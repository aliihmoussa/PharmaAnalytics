"""Data upload feature exceptions."""

from backend.app.shared.exceptions import AppException, NotFoundError


class DataUploadException(AppException):
    """Base exception for data upload errors."""
    pass


class FileValidationError(DataUploadException):
    """File validation failed."""
    status_code = 400
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class UnsupportedFileTypeError(FileValidationError):
    """Unsupported file type."""
    pass


class FileSizeLimitExceededError(FileValidationError):
    """File size exceeds limit."""
    pass


class IngestionJobNotFoundError(NotFoundError):
    """Ingestion job not found."""
    pass


class IngestionJobCancelledError(DataUploadException):
    """Ingestion job was cancelled."""
    status_code = 400


class DuplicateFileError(DataUploadException):
    """File already ingested."""
    status_code = 409


class IngestionProcessingError(DataUploadException):
    """Error during ingestion processing."""
    status_code = 500

