"""Tests for local SQLite database operations and multi-tenant isolation."""

import pytest
from sqlalchemy import select
from app.infrastructure.database import async_session_factory, init_db
from app.infrastructure.models import Document, DocumentStatus, Organization


@pytest.mark.asyncio
async def test_init_db_and_organization_creation():
    await init_db()

    async with async_session_factory() as session:
        # Create test organization
        org = Organization(id="test-org-123", name="Test Org Local")
        session.add(org)
        await session.commit()

        # Create test document
        doc = Document(
            id="doc-test-1",
            organization_id="test-org-123",
            filename="invoices.csv",
            file_size_bytes=1024,
            mime_type="text/csv",
            storage_path="./data/storage/test-org-123/doc-test-1/invoices.csv",
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        await session.commit()

        # Query back and verify multi-tenant isolation
        stmt = select(Document).where(
            Document.id == "doc-test-1",
            Document.organization_id == "test-org-123",
        )
        result = await session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved is not None
        assert retrieved.filename == "invoices.csv"
        assert retrieved.status == DocumentStatus.PENDING

        # Query with wrong organization ID should return None
        stmt_wrong = select(Document).where(
            Document.id == "doc-test-1",
            Document.organization_id == "other-org-999",
        )
        res_wrong = await session.execute(stmt_wrong)
        assert res_wrong.scalar_one_or_none() is None
