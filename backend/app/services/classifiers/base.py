"""Base abstract class for document classification engines."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.domain.schemas import ClassificationResult


class BaseClassifier(ABC):
    """Abstract interface for classification models."""

    @abstractmethod
    def classify(
        self,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """Categorizes document text into a standard DocumentType."""
        pass
