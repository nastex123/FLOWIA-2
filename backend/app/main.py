"""FlowMind AI Backend - FastAPI Application Entrypoint."""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import DocumentValidationError, ExtractionError
from app.core.logging import logger
from app.domain.schemas import ExtractionResult
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor

app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first intelligent business process automation (100% Local ML & Deterministic Processing)",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize extraction services
tabular_extractor = TabularExtractor()
pdf_extractor = PDFExtractor()


@app.get("/health", tags=["System"])
async def health_check():
    """Healthcheck endpoint for container orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "ai_engine": "pure_libraries_local",
    }


@app.post(
    "/api/v1/extract",
    response_model=ExtractionResult,
    tags=["Extraction"],
    status_code=status.HTTP_200_OK,
)
async def extract_document(
    file: UploadFile = File(..., description="Spreadsheet (XLSX, CSV) or PDF document"),
):
    """Uploads and processes a business document using pure local Python extractors."""
    filename = file.filename or "unnamed_document"
    ext = Path(filename).suffix.lower().lstrip(".")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '.{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    logger.info(f"Processing document: {filename} ({len(content)} bytes)")

    try:
        if ext in ("xlsx", "xls", "csv"):
            result = tabular_extractor.extract(
                file_input=content,
                filename=filename,
            )
        elif ext == "pdf":
            result = pdf_extractor.extract(
                file_input=content,
                filename=filename,
            )
        else:
            raise DocumentValidationError(f"No extractor available for .{ext}")

        return result
    except ExtractionError as e:
        logger.error(f"Extraction error for '{filename}': {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Extraction failed: {e.message}",
        )
    except Exception as e:
        logger.exception(f"Unexpected error processing '{filename}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal processing error occurred.",
        )
