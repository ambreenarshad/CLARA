"""Custom exceptions for the NLP Agentic AI system."""

from typing import Optional


class NLPAgenticError(Exception):
    """Base exception for all NLP Agentic AI errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Optional detailed information
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class DataIngestionError(NLPAgenticError):
    """Exception raised during data ingestion."""

    pass


class ValidationError(NLPAgenticError):
    """Exception raised during data validation."""

    pass


class AnalysisError(NLPAgenticError):
    """Exception raised during analysis operations."""

    pass


class RetrievalError(NLPAgenticError):
    """Exception raised during retrieval operations."""

    pass


class SynthesisError(NLPAgenticError):
    """Exception raised during synthesis operations."""

    pass


class ModelLoadError(NLPAgenticError):
    """Exception raised when loading NLP models fails."""

    pass


class VectorStoreError(NLPAgenticError):
    """Exception raised during vector store operations."""

    pass


class ConfigurationError(NLPAgenticError):
    """Exception raised for configuration errors."""

    pass


class FeedbackNotFoundError(NLPAgenticError):
    """Exception raised when feedback ID is not found."""

    def __init__(self, feedback_id: str):
        """
        Initialize exception.

        Args:
            feedback_id: Feedback ID that was not found
        """
        super().__init__(
            message=f"Feedback not found: {feedback_id}",
            details="The requested feedback ID does not exist in the database",
        )
        self.feedback_id = feedback_id


class InsufficientDataError(NLPAgenticError):
    """Exception raised when insufficient data is provided."""

    def __init__(self, required: int, provided: int):
        """
        Initialize exception.

        Args:
            required: Required number of items
            provided: Number of items provided
        """
        super().__init__(
            message=f"Insufficient data: need {required}, got {provided}",
            details=f"Operation requires at least {required} items",
        )
        self.required = required
        self.provided = provided
