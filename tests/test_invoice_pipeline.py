"""Tests for the integrated invoice processing and validation pipeline."""

import os
from pathlib import Path
import pytest
from sqlalchemy import select

from app.infrastructure.database import async_session_factory
from app.infrastructure.models import (
    Document,
    DocumentCheck,
    DocumentStatus,
    EntityRecord,
    ExtractionRecord,
    InvoiceFingerprint,
)
from app.services.pipeline import process_document_pipeline


@pytest.mark.asyncio
async def test_process_invoice_pipeline_generates_checks_and_structured_json(tmp_path):
    # Create sample CSV invoice file
    csv_content = (
        "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
        "INV-2024-001;2024-06-15;Acme Corp SL;B87654321;1000,00;1210,00\n"
    )
    file_path = tmp_path / "factura_test.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    doc_id = "doc-invoice-test-1"
    org_id = "default-org"

    async with async_session_factory() as session:
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename="factura_test.csv",
            file_size_bytes=len(csv_content),
            mime_type="text/csv",
            storage_path=str(file_path),
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        await session.commit()

    # Run pipeline
    await process_document_pipeline(
        document_id=doc_id,
        organization_id=org_id,
        file_path=file_path,
        filename="factura_test.csv",
    )

    async with async_session_factory() as session:
        # Verify document status
        updated_doc = (await session.execute(
            select(Document).where(Document.id == doc_id)
        )).scalar_one()
        assert updated_doc.status == DocumentStatus.COMPLETED
        assert updated_doc.review_status == "unreviewed"

        # Verify extraction record has structured_json
        ext_record = (await session.execute(
            select(ExtractionRecord).where(ExtractionRecord.document_id == doc_id)
        )).scalar_one()
        assert ext_record.structured_json is not None
        assert ext_record.structured_json["document_id"] == doc_id

        # Verify checks were persisted
        checks = (await session.execute(
            select(DocumentCheck).where(DocumentCheck.document_id == doc_id)
        )).scalars().all()
        assert len(checks) >= 1

        check_types = [c.check_type for c in checks]
        assert "math_discrepancy" in check_types

        # Verify fingerprint was saved
        fps = (await session.execute(
            select(InvoiceFingerprint).where(InvoiceFingerprint.document_id == doc_id)
        )).scalars().all()
        assert len(fps) == 1


@pytest.mark.asyncio
async def test_duplicate_invoice_detection(tmp_path):
    csv_content = (
        "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
        "INV-DUP-999;2024-06-15;Acme Corp SL;B87654321;1000,00;1210,00\n"
    )
    file_path1 = tmp_path / "factura_dup1.csv"
    file_path1.write_text(csv_content, encoding="utf-8")
    file_path2 = tmp_path / "factura_dup2.csv"
    file_path2.write_text(csv_content, encoding="utf-8")

    doc1_id = "doc-dup-1"
    doc2_id = "doc-dup-2"
    org_id = "default-org"

    # Insert doc 1
    async with async_session_factory() as session:
        doc1 = Document(
            id=doc1_id,
            organization_id=org_id,
            filename="factura_dup1.csv",
            file_size_bytes=len(csv_content),
            mime_type="text/csv",
            storage_path=str(file_path1),
            status=DocumentStatus.PENDING,
        )
        session.add(doc1)
        await session.commit()

    await process_document_pipeline(
        document_id=doc1_id,
        organization_id=org_id,
        file_path=file_path1,
        filename="factura_dup1.csv",
    )

    # Insert doc 2 (duplicate)
    async with async_session_factory() as session:
        doc2 = Document(
            id=doc2_id,
            organization_id=org_id,
            filename="factura_dup2.csv",
            file_size_bytes=len(csv_content),
            mime_type="text/csv",
            storage_path=str(file_path2),
            status=DocumentStatus.PENDING,
        )
        session.add(doc2)
        await session.commit()

    await process_document_pipeline(
        document_id=doc2_id,
        organization_id=org_id,
        file_path=file_path2,
        filename="factura_dup2.csv",
    )

    async with async_session_factory() as session:
        doc2_checks = (await session.execute(
            select(DocumentCheck).where(DocumentCheck.document_id == doc2_id)
        )).scalars().all()

        critical_checks = [c for c in doc2_checks if c.severity == "critical"]
        assert len(critical_checks) >= 1
        dup_check = next((c for c in critical_checks if c.check_type == "duplicate_invoice"), None)
        assert dup_check is not None
        assert "Factura duplicada" in dup_check.title
