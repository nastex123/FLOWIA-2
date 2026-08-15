"""Tests for PDFExtractor validation and parsing."""

import pytest
from app.core.exceptions import ExtractionError
from app.services.extractors.pdf_extractor import PDFExtractor


def test_pdf_extractor_invalid_header():
    extractor = PDFExtractor()
    with pytest.raises(ExtractionError, match="not a valid PDF document"):
        extractor.extract(
            file_input=b"Random non-pdf binary content",
            filename="corrupt.pdf",
        )
