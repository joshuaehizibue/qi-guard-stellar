"""
Custom exceptions for the QI-Guard Python SDK.
"""

from typing import Optional, Any


class QIGuardError(Exception):
    """Base exception for all QI-Guard SDK errors."""
    pass


class QIGuardAPIError(QIGuardError):
    """Raised when the QI-Guard API returns an HTTP error status."""
    def __init__(self, message: str, status_code: int, response_body: Optional[Any] = None):
        super().__init__(f"QI-Guard API Error [{status_code}]: {message}")
        self.status_code = status_code
        self.response_body = response_body


class QIGuardAuthenticationError(QIGuardAPIError):
    """Raised when the provided API key is invalid or unauthorized."""
    pass


class QIGuardRateLimitError(QIGuardAPIError):
    """Raised when monthly quota or request rate limit is exceeded."""
    pass
