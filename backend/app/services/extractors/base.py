"""Base abstract class for document extractors."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Union
from pathlib import Path

from app.domain.schemas import ExtractionResult


class BaseExtractor(ABC):
    """Abstract interface for all file and content extraction engines."""

    @abstractmethod
    def extract(
        self,
        file_input: Union[str, Path, bytes, BinaryIO],
        filename: str,
        document_id: Optional[str] = None,
        **kwargs,
    ) -> ExtractionResult:
        """Extracts structured entities, tables and metadata from the document."""
        pass
