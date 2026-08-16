"""Document ingestion, retrieval and normalization endpoints."""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthContext, require_editor_or_api_key, resolve_auth
from app.core.config import settings
from app.core.exceptions import DocumentValidationError, ExtractionError
from app.domain.schema_models import (
    AutoMapResponse,
    AutoMapSuggestion,
    NormalizedDatasetResponse,
    NormalizeRequest,
)
from app.domain.schemas import ExtractionResult
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Document,
    DocumentStatus,
    Organization,
    SchemaDefinition,
)
from app.services.automation.runner import run_automation_for_document
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.mapping.schema_normalizer import SchemaNormalizer
from app.services.pipeline import process_document_pipeline
from app.services.storage.local_storage import LocalStorageService

router = APIRouter(prefix="/api/v1", tags=["Documents"])

storage_service = LocalStorageService()
tabular_extractor = TabularExtractor()
pdf_extractor = PDFExtractor()
schema_normalizer = SchemaNormalizer()

MAX_NORMALIZED_SAMPLE_ROWS = 100


@router.post(
    "/documents/upload",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Spreadsheet (XLSX, CSV) or PDF document"),
    auth: AuthContext = Depends(require_editor_or_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Uploads a document, saves it to tenant storage, and enqueues async background extraction."""
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

    organization_id = auth.org_id

    # Ensure organization exists
    stmt_org = select(Organization).where(Organization.id == organization_id)
    result_org = await db.execute(stmt_org)
    org = result_org.scalar_one_or_none()
    if not org:
        org = Organization(id=organization_id, name="Default Organization")
        db.add(org)
        await db.commit()

    document_id = str(uuid.uuid4())

    # 1. Save file to local storage
    saved_path = storage_service.save_file(
        content=content,
        organization_id=organization_id,
        document_id=document_id,
        filename=filename,
    )

    # 2. Register document in database
    doc = Document(
        id=document_id,
        organization_id=organization_id,
        filename=filename,
        file_size_bytes=len(content),
        mime_type=file.content_type or "application/octet-stream",
        storage_path=str(saved_path),
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.commit()

    # 3. Enqueue background pipeline task
    background_tasks.add_task(
        process_document_pipeline,
        document_id=document_id,
        organization_id=organization_id,
        file_path=saved_path,
        filename=filename,
    )

    return {
        "document_id": document_id,
        "organization_id": organization_id,
        "filename": filename,
        "status": DocumentStatus.PENDING.value,
        "message": "Document uploaded successfully and queued for local extraction.",
    }


@router.get(
    "/documents/{document_id}",
)
async def get_document_details(
    document_id: str,
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves document processing status and extracted structured data."""
    stmt = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == document_id,
            Document.organization_id == auth.org_id,
        )
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    response = {
        "document_id": doc.id,
        "organization_id": doc.organization_id,
        "filename": doc.filename,
        "file_size_bytes": doc.file_size_bytes,
        "status": doc.status.value,
        "created_at": doc.created_at.isoformat(),
        "error_message": doc.error_message,
        "extraction": None,
    }

    if doc.extraction_record:
        rec = doc.extraction_record
        response["extraction"] = {
            "document_type": rec.document_type,
            "confidence": rec.confidence,
            "fields": rec.fields_json,
            "tables": rec.tables_json,
            "summary": rec.raw_summary,
            "processing_time_ms": rec.processing_time_ms,
        }

    return response


@router.get(
    "/documents",
)
async def list_documents(
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Lists all uploaded documents for the requesting organization."""
    stmt = (
        select(Document)
        .where(Document.organization_id == auth.org_id)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    docs = result.scalars().all()

    return [
        {
            "document_id": d.id,
            "filename": d.filename,
            "file_size_bytes": d.file_size_bytes,
            "status": d.status.value,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post(
    "/extract",
    response_model=ExtractionResult,
    tags=["Extraction"],
    status_code=status.HTTP_200_OK,
)
async def extract_document_direct(
    file: UploadFile = File(..., description="Spreadsheet (XLSX, CSV) or PDF document"),
    auth: AuthContext = Depends(require_editor_or_api_key),
):
    """Direct synchronous extraction test endpoint."""
    filename = file.filename or "unnamed_document"
    ext = Path(filename).suffix.lower().lstrip(".")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '.{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    try:
        if ext in ("xlsx", "xls", "csv"):
            return tabular_extractor.extract(file_input=content, filename=filename)
        elif ext == "pdf":
            return pdf_extractor.extract(file_input=content, filename=filename)
        else:
            raise DocumentValidationError(f"No extractor available for .{ext}")
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {e.message}")


# ==========================================
# Mapping & Normalization endpoints
# ==========================================


@router.post(
    "/documents/{document_id}/auto-map",
    response_model=AutoMapResponse,
    tags=["Mapping & Normalization"],
)
async def auto_map_document_columns(
    document_id: str,
    schema_id: str = Query(..., description="Target schema ID to match against"),
    table_index: int = Query(default=0, ge=0, description="Index of the extracted table"),
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Suggests fuzzy column pairings between document tables and a target schema."""
    doc = await _load_document_with_extraction(db, document_id, auth.org_id)
    schema_def = await _load_schema(db, schema_id, auth.org_id)

    tables = doc.extraction_record.tables_json or []
    if table_index >= len(tables):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table index {table_index} is out of bounds (found {len(tables)} tables).",
        )

    target_table = tables[table_index]
    source_columns = target_table.get("headers", [])

    suggestions = schema_normalizer.auto_suggest_mappings(
        source_columns=source_columns,
        schema_fields=schema_def.fields_config_json,
    )

    return AutoMapResponse(
        schema_id=schema_def.id,
        schema_name=schema_def.name,
        available_source_columns=source_columns,
        mappings=[AutoMapSuggestion(**s) for s in suggestions],
    )


@router.post(
    "/documents/{document_id}/normalize",
    response_model=NormalizedDatasetResponse,
    tags=["Mapping & Normalization"],
)
async def normalize_document(
    document_id: str,
    request: NormalizeRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Applies confirmed column mapping, produces a standardized dataset and triggers automation."""
    doc = await _load_document_with_extraction(db, document_id, auth.org_id)
    schema_def = await _load_schema(db, request.schema_id, auth.org_id)

    tables = doc.extraction_record.tables_json or []
    if request.table_index >= len(tables):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table index {request.table_index} is out of bounds.",
        )

    target_table = tables[request.table_index]
    source_records = target_table.get("records", [])

    normalized_records, val_errors = schema_normalizer.normalize_records(
        source_records=source_records,
        column_mapping=request.column_mapping,
        schema_fields=schema_def.fields_config_json,
    )

    schema_headers = [f["name"] for f in schema_def.fields_config_json]

    # Fire business automation rules for the normalization event (async, non-blocking)
    background_tasks.add_task(
        run_automation_for_document,
        event="normalization_completed",
        document_id=document_id,
        organization_id=auth.org_id,
        filename=doc.filename,
        document_type=doc.extraction_record.document_type,
        fields=doc.extraction_record.fields_json,
        normalized_context={
            "schema_id": schema_def.id,
            "schema_name": schema_def.name,
            "total_records": len(normalized_records),
            "headers": schema_headers,
            "records": normalized_records[:MAX_NORMALIZED_SAMPLE_ROWS],
            "validation_errors_count": len(val_errors),
        },
    )

    return NormalizedDatasetResponse(
        schema_id=schema_def.id,
        schema_name=schema_def.name,
        total_records=len(normalized_records),
        headers=schema_headers,
        records=normalized_records,
        validation_errors=val_errors,
    )


async def _load_document_with_extraction(
    db: AsyncSession, document_id: str, organization_id: str
) -> Document:
    stmt = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == document_id,
            Document.organization_id == organization_id,
        )
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc or not doc.extraction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or extraction record not found.",
        )
    return doc


async def _load_schema(
    db: AsyncSession, schema_id: str, organization_id: str
) -> SchemaDefinition:
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        (SchemaDefinition.organization_id == organization_id)
        | (SchemaDefinition.organization_id == "default-org"),
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target schema '{schema_id}' not found.",
        )
    return schema_def