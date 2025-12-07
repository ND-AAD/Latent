"""Custom exceptions for the analysis service."""


class AnalysisError(Exception):
    """Base exception for analysis errors."""
    pass


class InvalidCageError(AnalysisError):
    """Raised when control cage data is invalid."""
    pass


class LensError(AnalysisError):
    """Raised when lens analysis fails."""
    pass


class BoundaryExtractionError(AnalysisError):
    """Raised when boundary curve extraction fails."""
    pass


class ServiceNotInitializedError(AnalysisError):
    """Raised when service is used before initialization."""
    pass
