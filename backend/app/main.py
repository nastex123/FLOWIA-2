"""FlowMind AI Backend - FastAPI Application with local SQLite persistence and async pipeline."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import BackgroundTasks, Depends, FastAPI, File, Header, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import DocumentValidationError, ExtractionError
from app.core.logging import logger
from app.domain.schemas import ExtractionResult
from app.infrastructure.database import get_db, init_db
from app.infrastructure.models import Document, DocumentStatus, ExtractionRecord, Organization
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.pipeline import process_document_pipeline
from app.services.storage.local_storage import LocalStorageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Starting FlowMind AI backend in 100% Local Mode...")
    await init_db()
    yield
    logger.info("Shutting down FlowMind AI backend.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-first intelligent business process automation (100% Local ML, SQLite & Deterministic Processing)",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage & extractors singletons
storage_service = LocalStorageService()
tabular_extractor = TabularExtractor()
pdf_extractor = PDFExtractor()


@app.get("/health", tags=["System"])
async def health_check():
    """Healthcheck endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "storage": settings.STORAGE_BACKEND,
        "database": "sqlite_async" if "sqlite" in settings.DATABASE_URL else "postgresql",
        "ai_engine": "pure_libraries_local",
    }


@app.post(
    "/api/v1/documents/upload",
    tags=["Documents"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Spreadsheet (XLSX, CSV) or PDF document"),
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
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

    # Ensure organization exists
    stmt_org = select(Organization).where(Organization.id == x_organization_id)
    result_org = await db.execute(stmt_org)
    org = result_org.scalar_one_or_none()
    if not org:
        org = Organization(id=x_organization_id, name="Default Organization")
        db.add(org)
        await db.commit()

    document_id = str(uuid.uuid4())

    # 1. Save file to local storage
    saved_path = storage_service.save_file(
        content=content,
        organization_id=x_organization_id,
        document_id=document_id,
        filename=filename,
    )

    # 2. Register document in database
    doc = Document(
        id=document_id,
        organization_id=x_organization_id,
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
        organization_id=x_organization_id,
        file_path=saved_path,
        filename=filename,
    )

    return {
        "document_id": document_id,
        "organization_id": x_organization_id,
        "filename": filename,
        "status": DocumentStatus.PENDING.value,
        "message": "Document uploaded successfully and queued for local extraction.",
    }


@app.get(
    "/api/v1/documents/{document_id}",
    tags=["Documents"],
)
async def get_document_details(
    document_id: str,
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves document processing status and extracted structured data."""
    stmt = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == document_id,
            Document.organization_id == x_organization_id,
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


@app.get(
    "/api/v1/documents",
    tags=["Documents"],
)
async def list_documents(
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Lists all uploaded documents for the requesting organization."""
    stmt = (
        select(Document)
        .where(Document.organization_id == x_organization_id)
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


@app.post(
    "/api/v1/extract",
    response_model=ExtractionResult,
    tags=["Extraction"],
    status_code=status.HTTP_200_OK,
)
async def extract_document_direct(
    file: UploadFile = File(..., description="Spreadsheet (XLSX, CSV) or PDF document"),
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
# Schema Definitions & Normalization Endpoints
# ==========================================

from app.domain.schema_models import (
    AutoMapResponse,
    AutoMapSuggestion,
    NormalizedDatasetResponse,
    NormalizeRequest,
    SchemaCreate,
    SchemaResponse,
    SchemaUpdate,
)
from app.infrastructure.models import SchemaDefinition
from app.services.mapping.schema_normalizer import SchemaNormalizer

schema_normalizer = SchemaNormalizer()


@app.get(
    "/api/v1/schemas",
    response_model=List[SchemaResponse],
    tags=["Schemas"],
)
async def list_schemas(
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Lists all active schema definitions for the organization."""
    stmt = (
        select(SchemaDefinition)
        .where(
            (SchemaDefinition.organization_id == x_organization_id)
            | (SchemaDefinition.organization_id == "default-org")
        )
        .order_by(SchemaDefinition.created_at.asc())
    )
    result = await db.execute(stmt)
    schemas = result.scalars().all()

    return [
        SchemaResponse(
            id=s.id,
            organization_id=s.organization_id,
            name=s.name,
            description=s.description,
            document_type=s.document_type,
            fields=s.fields_config_json,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
        )
        for s in schemas
    ]


@app.post(
    "/api/v1/schemas",
    response_model=SchemaResponse,
    tags=["Schemas"],
    status_code=status.HTTP_201_CREATED,
)
async def create_schema(
    schema_in: SchemaCreate,
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new canonical data schema for an organization."""
    import uuid

    fields_data = [f.model_dump() for f in schema_in.fields]
    schema_id = str(uuid.uuid4())

    new_schema = SchemaDefinition(
        id=schema_id,
        organization_id=x_organization_id,
        name=schema_in.name,
        description=schema_in.description,
        document_type=schema_in.document_type,
        fields_config_json=fields_data,
    )
    db.add(new_schema)
    await db.commit()
    await db.refresh(new_schema)

    return SchemaResponse(
        id=new_schema.id,
        organization_id=new_schema.organization_id,
        name=new_schema.name,
        description=new_schema.description,
        document_type=new_schema.document_type,
        fields=new_schema.fields_config_json,
        created_at=new_schema.created_at.isoformat(),
        updated_at=new_schema.updated_at.isoformat(),
    )


@app.get(
    "/api/v1/schemas/{schema_id}",
    response_model=SchemaResponse,
    tags=["Schemas"],
)
async def get_schema_detail(
    schema_id: str,
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a specific schema definition."""
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        (SchemaDefinition.organization_id == x_organization_id)
        | (SchemaDefinition.organization_id == "default-org"),
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()

    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_id}' not found.",
        )

    return SchemaResponse(
        id=schema_def.id,
        organization_id=schema_def.organization_id,
        name=schema_def.name,
        description=schema_def.description,
        document_type=schema_def.document_type,
        fields=schema_def.fields_config_json,
        created_at=schema_def.created_at.isoformat(),
        updated_at=schema_def.updated_at.isoformat(),
    )


@app.delete(
    "/api/v1/schemas/{schema_id}",
    tags=["Schemas"],
    status_code=status.HTTP_200_OK,
)
async def delete_schema(
    schema_id: str,
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a custom schema definition."""
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        SchemaDefinition.organization_id == x_organization_id,
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()

    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_id}' not found or cannot be deleted.",
        )

    await db.delete(schema_def)
    await db.commit()
    return {"status": "deleted", "schema_id": schema_id}


@app.post(
    "/api/v1/documents/{document_id}/auto-map",
    response_model=AutoMapResponse,
    tags=["Mapping & Normalization"],
)
async def auto_map_document_columns(
    document_id: str,
    schema_id: str = Query(..., description="Target schema ID to match against"),
    table_index: int = Query(default=0, ge=0, description="Index of the extracted table"),
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Suggests fuzzy column pairings between document tables and a target schema."""
    # 1. Fetch document
    stmt_doc = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == document_id,
            Document.organization_id == x_organization_id,
        )
    )
    res_doc = await db.execute(stmt_doc)
    doc = res_doc.scalar_one_or_none()
    if not doc or not doc.extraction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or extraction record not found.",
        )

    # 2. Fetch schema
    stmt_schema = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        (SchemaDefinition.organization_id == x_organization_id)
        | (SchemaDefinition.organization_id == "default-org"),
    )
    res_schema = await db.execute(stmt_schema)
    schema_def = res_schema.scalar_one_or_none()
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target schema '{schema_id}' not found.",
        )

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


@app.post(
    "/api/v1/documents/{document_id}/normalize",
    response_model=NormalizedDatasetResponse,
    tags=["Mapping & Normalization"],
)
async def normalize_document(
    document_id: str,
    request: NormalizeRequest,
    x_organization_id: Optional[str] = Header(default="default-org", alias="X-Organization-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Applies confirmed column mapping and produces a standardized dataset."""
    # 1. Fetch document
    stmt_doc = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == document_id,
            Document.organization_id == x_organization_id,
        )
    )
    res_doc = await db.execute(stmt_doc)
    doc = res_doc.scalar_one_or_none()
    if not doc or not doc.extraction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or extraction record not found.",
        )

    # 2. Fetch schema
    stmt_schema = select(SchemaDefinition).where(
        SchemaDefinition.id == request.schema_id,
        (SchemaDefinition.organization_id == x_organization_id)
        | (SchemaDefinition.organization_id == "default-org"),
    )
    res_schema = await db.execute(stmt_schema)
    schema_def = res_schema.scalar_one_or_none()
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target schema '{request.schema_id}' not found.",
        )

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

    return NormalizedDatasetResponse(
        schema_id=schema_def.id,
        schema_name=schema_def.name,
        total_records=len(normalized_records),
        headers=schema_headers,
        records=normalized_records,
        validation_errors=val_errors,
    )
