"""Asynchronous background worker tasks for FlowMind AI."""

from typing import Any, Dict
from pathlib import Path

# Note: In production, tasks are consumed from Redis queue via ARQ / Celery
# This module provides the task definitions and pure library worker execution logic


async def process_document_job(
    document_id: str,
    file_path: str,
    filename: str,
    organization_id: str,
) -> Dict[str, Any]:
    """Background task to extract and classify a document asynchronously."""
    # Delayed imports to keep worker startup light
    from app.services.extractors.tabular_extractor import TabularExtractor
    from app.services.extractors.pdf_extractor import PDFExtractor

    ext = Path(filename).suffix.lower().lstrip(".")
    path_obj = Path(file_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Document file not found at {file_path}")

    if ext in ("xlsx", "xls", "csv"):
        extractor = TabularExtractor()
    elif ext == "pdf":
        extractor = PDFExtractor()
    else:
        raise ValueError(f"Unsupported format: {ext}")

    result = extractor.extract(
        file_input=path_obj,
        filename=filename,
        document_id=document_id,
    )

    return result.model_dump()
