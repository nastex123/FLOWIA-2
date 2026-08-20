"""Integration tests for the Invoice Review API and multi-tenant isolation."""

import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.infrastructure.database import async_session_factory
from app.infrastructure.models import (
    Document,
    DocumentCheck,
    DocumentStatus,
    ExtractionRecord,
    Organization,
    User,
    UserRole,
)
from app.core.security import hash_password, create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_get_documents_with_check_summary(auth_client):
    doc_id = "doc-summary-test-1"
    org_id = "default-org"

    async with async_session_factory() as session:
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename="factura_summary.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            storage_path="/tmp/test.pdf",
            status=DocumentStatus.COMPLETED,
            review_status="unreviewed",
        )
        session.add(doc)

        # Add checks with different severities
        chk_ok = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="math_discrepancy",
            severity="ok",
            status="open",
            title="Total recalculado correctamente",
        )
        chk_warn = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="threshold_avoidance",
            severity="warning",
            status="open",
            title="Importe próximo a umbral",
        )
        chk_crit = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="bank_account_change",
            severity="critical",
            status="open",
            title="Nuevo IBAN detectado",
        )
        session.add_all([chk_ok, chk_warn, chk_crit])
        await session.commit()

    response = await auth_client.get("/api/v1/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1

    target = next((d for d in docs if d["document_id"] == doc_id), None)
    assert target is not None
    assert target["review_status"] == "unreviewed"
    assert target["check_summary"] == {
        "ok": 1,
        "warning": 1,
        "critical": 1,
        "info": 0,
    }


@pytest.mark.asyncio
async def test_get_document_details_with_structured_invoice_and_checks(auth_client):
    doc_id = "doc-detail-test-1"
    org_id = "default-org"

    structured_inv = {
        "document_id": doc_id,
        "invoice_number": "INV-2024-88",
        "vendor_name": "Suministros Tech S.L.",
        "vendor_tax_id": "B12345678",
        "issue_date": "2024-06-18",
        "currency": "EUR",
        "subtotal": 1000.0,
        "tax_total": 210.0,
        "total_amount": 1210.0,
        "items": [
            {
                "description": "Servidor Cloud",
                "quantity": 1.0,
                "unit_price": 1000.0,
                "tax_rate_pct": 21.0,
                "line_total": 1000.0,
            }
        ],
        "tax_breakdown": [
            {
                "tax_rate_pct": 21.0,
                "taxable_base": 1000.0,
                "tax_quota": 210.0,
            }
        ],
    }

    async with async_session_factory() as session:
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename="factura_detail.pdf",
            file_size_bytes=2048,
            mime_type="application/pdf",
            storage_path="/tmp/detail.pdf",
            status=DocumentStatus.COMPLETED,
            review_status="unreviewed",
        )
        session.add(doc)

        ext = ExtractionRecord(
            document_id=doc_id,
            organization_id=org_id,
            document_type="invoice",
            confidence=0.98,
            fields_json={"invoice_number": "INV-2024-88"},
            tables_json=[],
            structured_json=structured_inv,
        )
        session.add(ext)

        chk = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="math_discrepancy",
            severity="critical",
            status="open",
            title="Diferencia de 10€ en el total",
            detail_json={"deviation": 10.0},
        )
        session.add(chk)
        await session.commit()

    response = await auth_client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == doc_id
    assert data["status"] == "completed"
    assert data["review_status"] == "unreviewed"
    assert data["structured_invoice"] is not None
    assert data["structured_invoice"]["invoice_number"] == "INV-2024-88"
    assert len(data["checks"]) == 1
    assert data["checks"][0]["check_type"] == "math_discrepancy"
    assert data["checks"][0]["severity"] == "critical"


@pytest.mark.asyncio
async def test_review_document_action(auth_client):
    doc_id = "doc-review-action-1"
    org_id = "default-org"

    async with async_session_factory() as session:
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename="factura_review.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            storage_path="/tmp/review.pdf",
            status=DocumentStatus.COMPLETED,
            review_status="unreviewed",
        )
        session.add(doc)

        chk = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="math_discrepancy",
            severity="warning",
            status="open",
            title="Diferencia de redondeo 0.05€",
        )
        session.add(chk)
        await session.commit()

    # Review document
    response = await auth_client.post(
        f"/api/v1/documents/{doc_id}/review",
        json={"note": "Aprobado por el departamento contable"},
    )
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status"] == "reviewed"
    assert res_data["document_id"] == doc_id
    assert res_data["acknowledged_checks_count"] == 1
    assert res_data["reviewed_by"] is not None

    # Check updated database state
    async with async_session_factory() as session:
        updated_doc = (await session.execute(
            select(Document).where(Document.id == doc_id)
        )).scalar_one()
        assert updated_doc.review_status == "reviewed"
        assert updated_doc.reviewed_at is not None

        updated_chk = (await session.execute(
            select(DocumentCheck).where(DocumentCheck.document_id == doc_id)
        )).scalar_one()
        assert updated_chk.status == "acknowledged"


@pytest.mark.asyncio
async def test_decision_checks_endpoint_filtering(auth_client):
    doc_id = "doc-checks-filter-1"
    org_id = "default-org"

    async with async_session_factory() as session:
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            filename="factura_checks.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            storage_path="/tmp/checks.pdf",
            status=DocumentStatus.COMPLETED,
        )
        session.add(doc)

        chk1 = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="math_discrepancy",
            severity="critical",
            status="open",
            title="Math error",
        )
        chk2 = DocumentCheck(
            organization_id=org_id,
            document_id=doc_id,
            check_type="duplicate_invoice",
            severity="warning",
            status="acknowledged",
            title="Potential duplicate",
        )
        session.add_all([chk1, chk2])
        await session.commit()

    # Filter by severity
    res_crit = await auth_client.get(f"/api/v1/decision/checks?document_id={doc_id}&severity=critical")
    assert res_crit.status_code == 200
    data_crit = res_crit.json()
    assert data_crit["total"] == 1
    assert data_crit["items"][0]["severity"] == "critical"
    assert data_crit["items"][0]["filename"] == "factura_checks.pdf"

    # Filter by status
    res_ack = await auth_client.get(f"/api/v1/decision/checks?document_id={doc_id}&status=acknowledged")
    assert res_ack.status_code == 200
    data_ack = res_ack.json()
    assert data_ack["total"] == 1
    assert data_ack["items"][0]["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_multi_tenant_isolation(auth_client):
    # Setup Tenant B and User B
    org_b_id = "tenant-b-org"
    user_b_id = "user-b-id"
    user_b_email = "finance@tenantb.com"
    user_b_pass = "tenantBpass123"

    async with async_session_factory() as session:
        org_b = Organization(id=org_b_id, name="Tenant B Corp")
        session.add(org_b)

        user_b = User(
            id=user_b_id,
            organization_id=org_b_id,
            email=user_b_email,
            hashed_password=hash_password(user_b_pass),
            role=UserRole.ADMIN,
        )
        session.add(user_b)

        # Create Document belonging to Org B
        doc_b = Document(
            id="doc-tenant-b-private",
            organization_id=org_b_id,
            filename="confidential_b.pdf",
            file_size_bytes=512,
            mime_type="application/pdf",
            storage_path="/tmp/confidential_b.pdf",
            status=DocumentStatus.COMPLETED,
        )
        session.add(doc_b)

        chk_b = DocumentCheck(
            organization_id=org_b_id,
            document_id="doc-tenant-b-private",
            check_type="math_discrepancy",
            severity="critical",
            status="open",
            title="Org B private check",
        )
        session.add(chk_b)
        await session.commit()

    # 1. Tenant A (auth_client) attempts to GET Org B's document -> 404
    res_detail = await auth_client.get("/api/v1/documents/doc-tenant-b-private")
    assert res_detail.status_code == 404

    # 2. Tenant A attempts to review Org B's document -> 404
    res_review = await auth_client.post(
        "/api/v1/documents/doc-tenant-b-private/review",
        json={"note": "Hacker note"},
    )
    assert res_review.status_code == 404

    # 3. Tenant A listing checks cannot see Org B's checks
    res_checks = await auth_client.get("/api/v1/decision/checks?document_id=doc-tenant-b-private")
    assert res_checks.status_code == 200
    assert res_checks.json()["total"] == 0
    assert len(res_checks.json()["items"]) == 0
