"""Simulated FlowMind backend used while P2 (invoice review API) is not merged.

Exposes the same JSON shapes defined in the TDD
(docs/04-engineering/04-invoice-validation-review.md, section 5) so the PySide6
desktop client and its tests can be built and run end-to-end today.

Once Luis merges P2, the real backend replaces this transport without any UI change.
"""

import json
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

import httpx

MOCK_DOCUMENT_ID = "8f8b8946-b6b8-4775-9b2f-981881775791"
MOCK_ORGANIZATION_ID = "default-org"
MOCK_API_KEY = "fm_q3PSywHmock"

MOCK_ORGANIZATIONS = [
    {"id": "default-org", "name": "Organización Principal"},
    {"id": "acme-org", "name": "Acme Corp S.L."},
]

MOCK_CHECK_SUMMARY = {"ok": 2, "warning": 1, "critical": 1, "info": 1}

MOCK_STRUCTURED_INVOICE = {
    "document_id": MOCK_DOCUMENT_ID,
    "invoice_number": "F-2024-0982",
    "vendor_name": "Suministros Industriales S.L.",
    "vendor_tax_id": "B12345678",
    "customer_name": "Construcciones del Norte S.A.",
    "customer_tax_id": "A11223344",
    "issue_date": "2024-06-18",
    "due_date": "2024-07-18",
    "currency": "EUR",
    "subtotal": 1250.50,
    "tax_total": 262.61,
    "total_amount": 1513.11,
    "withholding_amount": None,
    "shipping_amount": None,
    "items": [
        {
            "description": "Material oficina",
            "quantity": 10,
            "unit_price": 25.0,
            "discount_pct": None,
            "tax_rate_pct": 21.0,
            "line_total": 250.0,
        },
        {
            "description": "Equipos informáticos",
            "quantity": 2,
            "unit_price": 500.25,
            "discount_pct": None,
            "tax_rate_pct": 21.0,
            "line_total": 1000.50,
        },
    ],
    "tax_breakdown": [
        {"tax_rate_pct": 21.0, "taxable_base": 1250.50, "tax_quota": 262.61}
    ],
}

MOCK_CHECKS = [
    {
        "id": "check-001",
        "check_type": "math_discrepancy",
        "severity": "critical",
        "status": "open",
        "title": "El total del documento difiere del recálculo en 12.30 €",
        "detail_json": {"delta": 12.30},
        "created_at": "2026-08-18T09:30:00",
    },
    {
        "id": "check-002",
        "check_type": "bank_account_change",
        "severity": "critical",
        "status": "open",
        "title": "El IBAN del documento no existe en el histórico del proveedor",
        "detail_json": {"iban": "ES7621000418401234567891"},
        "created_at": "2026-08-18T09:30:01",
    },
    {
        "id": "check-003",
        "check_type": "entity_resolution",
        "severity": "info",
        "status": "open",
        "title": "Entidad vinculada: Suministros Industriales S.L.",
        "detail_json": {"entity_id": "ent-001"},
        "created_at": "2026-08-18T09:30:02",
    },
]

MOCK_DOCUMENTS = [
    {
        "document_id": MOCK_DOCUMENT_ID,
        "organization_id": MOCK_ORGANIZATION_ID,
        "filename": "factura_suministros_2024.xlsx",
        "status": "completed",
        "review_status": "unreviewed",
        "check_summary": MOCK_CHECK_SUMMARY,
        "created_at": "2026-08-15T21:00:00",
    },
    {
        "document_id": "8f8b8946-b6b8-4775-9b2f-981881775792",
        "organization_id": MOCK_ORGANIZATION_ID,
        "filename": "factura_limpieza_2024.pdf",
        "status": "completed",
        "review_status": "reviewed",
        "check_summary": {"ok": 3, "warning": 0, "critical": 0, "info": 1},
        "created_at": "2026-08-14T18:30:00",
    },
]


def _json_response(request: httpx.Request, data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code=status_code, json=data, request=request)


def mock_backend_handler(request: httpx.Request) -> httpx.Response:
    """Handles requests against the simulated backend following TDD section 5 shapes."""
    method = request.method.upper()
    url_str = str(request.url)
    parsed = urlparse(url_str)
    path = parsed.path

    if method == "POST" and path == "/api/v1/auth/login":
        payload = json.loads(request.content or b"{}")
        email = payload.get("email", "admin@flowmind.local")
        return _json_response(
            request,
            {
                "access_token": "mock-jwt-token",
                "token_type": "bearer",
                "expires_in_minutes": 1440,
                "user": {
                    "id": "user-001",
                    "email": email,
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2026-08-16T04:41:49",
                },
            },
        )

    if method == "GET" and path == "/api/v1/auth/me":
        return _json_response(
            request,
            {
                "user": {
                    "id": "user-001",
                    "email": "admin@flowmind.local",
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2026-08-16T04:41:49",
                },
                "default_organization": MOCK_ORGANIZATIONS[0],
                "organizations": MOCK_ORGANIZATIONS,
            },
        )

    if method == "POST" and path == "/api/v1/auth/api-keys":
        return _json_response(
            request,
            {
                "id": "apikey-001",
                "organization_id": MOCK_ORGANIZATION_ID,
                "name": "mock",
                "prefix": "fm_q3PSywH",
                "is_active": True,
                "last_used_at": None,
                "expires_at": None,
                "created_at": "2026-08-18T09:00:00",
                "key": MOCK_API_KEY,
            },
        )

    if method == "POST" and path == "/api/v1/documents/upload":
        return _json_response(
            request,
            {
                "document_id": MOCK_DOCUMENT_ID,
                "organization_id": MOCK_ORGANIZATION_ID,
                "filename": "uploaded_file",
                "status": "pending",
                "message": "Document uploaded successfully and queued for local extraction.",
            },
            status_code=202,
        )

    if method == "GET" and path == "/api/v1/documents":
        return _json_response(request, MOCK_DOCUMENTS)

    if method == "GET" and path == f"/api/v1/documents/{MOCK_DOCUMENT_ID}":
        return _json_response(
            request,
            {
                "document_id": MOCK_DOCUMENT_ID,
                "organization_id": MOCK_ORGANIZATION_ID,
                "filename": "factura_suministros_2024.xlsx",
                "status": "completed",
                "review_status": "unreviewed",
                "created_at": "2026-08-15T21:00:00",
                "error_message": None,
                "extraction": {
                    "document_type": "invoice",
                    "confidence": 0.95,
                    "fields": {},
                    "tables": [],
                    "summary": "mock",
                    "processing_time_ms": 42.5,
                },
                "structured_invoice": MOCK_STRUCTURED_INVOICE,
                "checks": MOCK_CHECKS,
            },
        )

    if method == "GET" and path == "/api/v1/decision/checks":
        query = parse_qs(parsed.query)
        items = MOCK_CHECKS
        if query.get("severity"):
            items = [c for c in items if c["severity"] == query["severity"][0]]
        if query.get("status"):
            items = [c for c in items if c["status"] == query["status"][0]]
        return _json_response(request, {"items": items, "total": len(items)})

    if method == "POST" and path == f"/api/v1/documents/{MOCK_DOCUMENT_ID}/review":
        return _json_response(
            request,
            {"status": "reviewed", "document_id": MOCK_DOCUMENT_ID},
        )

    return _json_response(
        request,
        {"detail": f"Simulated backend: {method} {path} no implementado."},
        status_code=404,
    )


def simulated_transport() -> httpx.MockTransport:
    return httpx.MockTransport(mock_backend_handler)


def build_simulated_client(base_url: str = "http://127.0.0.1:8000"):
    from desktop.controllers.api_client import DesktopFlowMindClient

    return DesktopFlowMindClient(base_url=base_url, transport=simulated_transport())