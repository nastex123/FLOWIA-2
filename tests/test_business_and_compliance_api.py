"""Integration tests for the Business Engines & Compliance REST APIs."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_three_way_match(auth_client: AsyncClient):
    payload = {
        "po_number": "PO-2024-001",
        "invoice_number": "FAC-2024-001",
        "lines": [
            {
                "sku": "ITEM-1",
                "description": "Item Alpha",
                "ordered_qty": 10.0,
                "received_qty": 10.0,
                "invoiced_qty": 10.0,
                "po_unit_price": 50.0,
                "invoice_unit_price": 50.0,
            }
        ],
    }

    response = await auth_client.post(
        "/api/v1/business/three-way-match",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["is_payable"] is True


@pytest.mark.asyncio
async def test_api_sii_xml_generation(auth_client: AsyncClient):
    payload = {
        "fiscal_year": 2024,
        "period": "06",
        "is_issued": True,
        "emitter_nif": "B12345678",
        "emitter_name": "Emisor S.L.",
        "counterparty_nif": "A87654321",
        "counterparty_name": "Receptor S.A.",
        "invoice_number": "FAC-2024-0099",
        "invoice_date": "2024-06-20",
        "total_amount": 605.00,
        "tax_breakdown": [
            {
                "tax_rate_pct": 21.0,
                "taxable_base": 500.00,
                "tax_quota": 105.00,
            }
        ],
    }

    response = await auth_client.post(
        "/api/v1/compliance/sii/generate-xml",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "SuministroLRFacturasEmitidas" in data["xml_content"]


@pytest.mark.asyncio
async def test_api_pii_redaction(auth_client: AsyncClient):
    payload = {
        "text": "Contacto del director: director@empresa.com con DNI 12345678Z",
        "mask_nif": True,
        "mask_email": True,
    }

    response = await auth_client.post(
        "/api/v1/compliance/pii/redact",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert "[REDACTED_EMAIL]" in data["sanitized_text"]
    assert "[REDACTED_NIF]" in data["sanitized_text"]
