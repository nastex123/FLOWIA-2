"""Tests for full local processing pipeline with SQLite and local disk storage."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.database import async_session_factory, init_db
from app.infrastructure.models import Document, DocumentStatus, Organization
from app.services.pipeline import process_document_pipeline
from app.services.storage.local_storage import LocalStorageService


@pytest.mark.asyncio
async def test_local_storage_and_pipeline_execution(sample_csv_invoice, tmp_path):
    await init_db()

    storage = LocalStorageService(base_path=tmp_path)
    org_id = "org-pipeline-test"
    doc_id = "doc-pipeline-test-001"
    filename = "test_invoices.csv"

    # Save to storage
    file_path = storage.save_file(
        content=sample_csv_invoice,
        organization_id=org_id,
        document_id=doc_id,
        filename=filename,
    )
    assert file_path.exists()

    async with async_session_factory() as session:
        # Create organization and document records
        org = Organization(id=org_id, name="Pipeline Test Org")
        session.add(org)
        await session.commit()

        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename=filename,
            file_size_bytes=len(sample_csv_invoice),
            mime_type="text/csv",
            storage_path=str(file_path),
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        await session.commit()

    # Run processing pipeline asynchronously
    await process_document_pipeline(
        document_id=doc_id,
        organization_id=org_id,
        file_path=file_path,
        filename=filename,
    )

    # Verify results in database
    async with async_session_factory() as session:
        stmt = (
            select(Document)
            .options(selectinload(Document.extraction_record))
            .where(Document.id == doc_id)
        )
        result = await session.execute(stmt)
        processed_doc = result.scalar_one()

        assert processed_doc.status == DocumentStatus.COMPLETED
        assert processed_doc.error_message is None
        assert processed_doc.extraction_record is not None

        rec = processed_doc.extraction_record
        assert rec.document_type == "invoice"
        assert "invoice_number" in rec.fields_json
        assert len(rec.tables_json) == 1
        assert rec.tables_json[0]["rows_count"] == 2
