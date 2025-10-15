"""
Custom exceptions for the One Trade application.
"""

from typing import Any, Dict, Optional


class OneTradeException(Exception):
    """Base exception for One Trade application."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "ONETRADE_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(OneTradeException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(OneTradeException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ExternalAPIError(OneTradeException):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            status_code=502,
            details=details,
        )


class DataProcessingError(OneTradeException):
    """Raised when data processing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATA_PROCESSING_ERROR",
            status_code=422,
            details=details,
        )


class RecommendationError(OneTradeException):
    """Raised when recommendation generation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RECOMMENDATION_ERROR",
            status_code=422,
            details=details,
        )


class BacktestError(OneTradeException):
    """Raised when backtesting fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BACKTEST_ERROR",
            status_code=422,
            details=details,
        )

