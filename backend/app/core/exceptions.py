"""Custom domain and infrastructure exceptions for FlowMind AI."""

from typing import Any, Optional


class FlowMindException(Exception):
    """Base exception for all FlowMind AI domain errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class DocumentValidationError(FlowMindException):
    """Raised when an uploaded document fails format, size or MIME checks."""
    pass


class ExtractionError(FlowMindException):
    """Raised when document parsing or field extraction fails."""
    pass


class ClassificationError(FlowMindException):
    """Raised when document categorization fails."""
    pass


class TenantAccessError(FlowMindException):
    """Raised when multi-tenant boundaries are violated."""
    pass
