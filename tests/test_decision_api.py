"""Integration tests for the Decision Engine REST API with database-backed persistence."""

from datetime import datetime
import pytest
from httpx import AsyncClient
from app.infrastructure.database import async_session_factory
from app.infrastructure.models import EntityRecord, InvoiceFingerprint


@pytest.mark.asyncio
async def test_api_validate_math_endpoint(auth_client: AsyncClient):
    payload = {
        "lines": [
            {
                "description": "Item A",
                "quantity": 10,
                "unit_price": 50.0,
                "tax_rate_pct": 21.0,
            }
        ],
        "document_subtotal": 500.0,
        "document_tax": 105.0,
        "document_total": 605.0,
    }

    response = await auth_client.post(
        "/api/v1/decision/validate-math",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["calculated_total"] == 605.0
    assert data["deviation"] == 0.0


@pytest.mark.asyncio
async def test_api_resolve_entity_endpoint(auth_client: AsyncClient):
    # Seed known entity into database for default-org
    async with async_session_factory() as session:
        ent = EntityRecord(
            organization_id="default-org",
            entity_id="ent-001",
            name="Suministros Industriales Iberica S.L.",
            tax_id="ESB12345678",
            ibans_json=["ES9121000418450200051332"],
            email_domain="suministros.es",
            phone="+34912345678",
        )
        session.add(ent)
        await session.commit()

    payload = {
        "name": "Suministros Industriales Iberica",
        "tax_id": "ESB12345678",
        "email_domain": "suministros.es",
    }

    response = await auth_client.post(
        "/api/v1/decision/entities/resolve",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "ent-001"
    assert data["action"] == "auto_merge"
    assert data["confidence_score"] >= 0.85


@pytest.mark.asyncio
async def test_api_sentinel_audit_endpoint(auth_client: AsyncClient):
    # Seed historical invoice fingerprint in database
    async with async_session_factory() as session:
        fp = InvoiceFingerprint(
            organization_id="default-org",
            document_id="doc-hist-001",
            fingerprint="test-fp-1",
            vendor_tax_id="ESB12345678",
            invoice_number="F-2024-001",
            invoice_date=datetime(2024, 5, 10),
            total_amount=1500.00,
        )
        ent = EntityRecord(
            organization_id="default-org",
            entity_id="ent-001",
            name="Suministros Industriales",
            tax_id="ESB12345678",
            ibans_json=["ES9121000418450200051332"],
        )
        session.add_all([fp, ent])
        await session.commit()

    payload = {
        "document_id": "doc-test-123",
        "vendor_tax_id": "ESB12345678",
        "invoice_number": "F-2024-001",
        "invoice_date": "2024-05-10",
        "total_amount": 1500.00,
        "iban": "ES9121000418450200051332",  # Valid historical IBAN
    }

    response = await auth_client.post(
        "/api/v1/decision/sentinel-audit",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    # It should detect exact duplicate against the historical record
    assert data["total_alerts"] >= 1
    assert any(a["alert_type"] == "multidimensional_duplicate" for a in data["alerts"])
