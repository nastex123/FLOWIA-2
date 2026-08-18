"""Desktop invoice review tests: simulated backend contract + real backend integration."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from anyio.from_thread import start_blocking_portal
from httpx import ASGITransport, BaseTransport, Request, Response
from PySide6.QtWidgets import QApplication

from desktop.controllers.api_client import DesktopFlowMindClient
from desktop.controllers.mock_backend import (
    MOCK_API_KEY,
    MOCK_DOCUMENT_ID,
    MOCK_ORGANIZATION_ID,
    build_simulated_client,
)

app = QApplication.instance() or QApplication([])


class SyncASGITransport(BaseTransport):
    """Bridges the synchronous httpx client to the real FastAPI ASGI app."""

    def __init__(self, application):
        self._application = application
        self._async_transport = ASGITransport(app=application)

    def handle_request(self, request: Request) -> Response:
        with start_blocking_portal() as portal:
            async_resp = portal.call(self._async_transport.handle_async_request, request)
            content = portal.call(async_resp.aread)
            return Response(
                status_code=async_resp.status_code,
                headers=async_resp.headers,
                content=content,
                request=request,
            )

    def close(self) -> None:
        pass


def _real_client() -> DesktopFlowMindClient:
    from app.main import app as backend_app

    return DesktopFlowMindClient(base_url="http://test", transport=SyncASGITransport(backend_app))


# ---------------------------------------------------------------------------
# Simulated backend (P2 contract per TDD section 5)
# ---------------------------------------------------------------------------


def test_simulated_login_and_me():
    client = build_simulated_client()
    response = client.login("admin@flowmind.local", "admin123")
    assert client.token == "mock-jwt-token"
    assert response["user"]["email"] == "admin@flowmind.local"

    me = client.me()
    assert len(me["organizations"]) == 2
    assert client.organization_id == "default-org"
    assert client.default_organization_id == "default-org"


def test_simulated_list_documents_contract():
    client = build_simulated_client()
    documents = client.list_documents()
    assert len(documents) == 2
    first = documents[0]
    assert first["document_id"] == MOCK_DOCUMENT_ID
    assert "check_summary" in first
    assert first["check_summary"]["critical"] == 1
    assert first["review_status"] == "unreviewed"


def test_simulated_get_document_contract():
    client = build_simulated_client()
    detail = client.get_document(MOCK_DOCUMENT_ID)
    invoice = detail["structured_invoice"]
    assert invoice["vendor_name"] == "Suministros Industriales S.L."
    assert invoice["vendor_tax_id"] == "B12345678"
    assert len(invoice["items"]) == 2
    assert invoice["items"][0]["line_total"] == 250.0
    assert invoice["tax_breakdown"][0]["tax_quota"] == 262.61
    checks = detail["checks"]
    assert any(c["severity"] == "critical" for c in checks)


def test_simulated_list_checks_filters():
    client = build_simulated_client()
    result = client.list_checks()
    assert result["total"] == 3

    filtered = client.list_checks(severity="critical", status="open")
    assert all(c["severity"] == "critical" for c in filtered["items"])
    assert filtered["total"] == 2


def test_simulated_review_document():
    client = build_simulated_client()
    result = client.review_document(MOCK_DOCUMENT_ID, note="Revisado por contabilidad")
    assert result["status"] == "reviewed"
    assert result["document_id"] == MOCK_DOCUMENT_ID


def test_simulated_upload_file(tmp_path):
    client = build_simulated_client()
    client.api_key = MOCK_API_KEY
    client.organization_id = MOCK_ORGANIZATION_ID
    file_path = tmp_path / "factura.csv"
    file_path.write_bytes(b"a,b\n1,2\n")

    result = client.upload_file(file_path)
    assert result["document_id"] == MOCK_DOCUMENT_ID
    assert result["status"] == "pending"


# ---------------------------------------------------------------------------
# Client header verification (contract between P3 and P2/P4)
# ---------------------------------------------------------------------------


def _client_with_captured_requests() -> tuple[DesktopFlowMindClient, list[Request]]:
    captured: list[Request] = []

    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(200, json={"ok": True}, request=request)

    client = DesktopFlowMindClient(base_url="http://test", transport=httpx.MockTransport(handler))
    return client, captured


def test_upload_sends_api_key_and_org_headers(tmp_path):
    client, captured = _client_with_captured_requests()
    client.api_key = MOCK_API_KEY
    client.organization_id = MOCK_ORGANIZATION_ID
    file_path = tmp_path / "factura.csv"
    file_path.write_bytes(b"a,b\n1,2\n")

    client.upload_file(file_path)

    assert len(captured) == 1
    headers = captured[0].headers
    assert headers["X-API-Key"] == MOCK_API_KEY
    assert headers["X-Organization-Id"] == MOCK_ORGANIZATION_ID
    assert "Authorization" not in headers


def test_documents_requests_send_bearer_and_org_headers():
    client, captured = _client_with_captured_requests()
    client.token = "jwt-token"
    client.organization_id = MOCK_ORGANIZATION_ID

    client.list_documents()

    assert len(captured) == 1
    headers = captured[0].headers
    assert headers["Authorization"] == "Bearer jwt-token"
    assert headers["X-Organization-Id"] == MOCK_ORGANIZATION_ID


# ---------------------------------------------------------------------------
# Real backend integration (endpoints already implemented)
# ---------------------------------------------------------------------------


def test_real_login_me_and_list():
    from app.core.config import settings

    client = _real_client()
    token_response = client.login(settings.DEFAULT_ADMIN_EMAIL, settings.DEFAULT_ADMIN_PASSWORD)
    assert client.token == token_response["access_token"]

    me = client.me()
    assert me["user"]["email"] == settings.DEFAULT_ADMIN_EMAIL
    assert client.organization_id == "default-org"

    documents = client.list_documents()
    assert isinstance(documents, list)


def test_real_upload_and_get_document(tmp_path):
    from app.core.config import settings

    client = _real_client()
    client.login(settings.DEFAULT_ADMIN_EMAIL, settings.DEFAULT_ADMIN_PASSWORD)

    file_path = tmp_path / "factura_test.csv"
    file_path.write_bytes(
        (
            "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
            "INV-2024-9999;2024-05-15;Acme Corp SL;B87654321;1000,00;1210,00\n"
        ).encode("utf-8")
    )

    result = client.upload_file(file_path)
    assert result["status"] == "pending"
    assert result["document_id"]

    documents = client.list_documents()
    assert any(d["document_id"] == result["document_id"] for d in documents)

    detail = client.get_document(result["document_id"])
    assert detail["filename"] == "factura_test.csv"


@pytest_asyncio.fixture
async def api_key_header(auth_client):
    response = await auth_client.post("/api/v1/auth/api-keys", json={"name": "desktop-test"})
    assert response.status_code == 201, response.text
    return {"X-API-Key": response.json()["key"], "X-Organization-Id": "default-org"}


@pytest.mark.asyncio
async def test_real_api_key_upload_endpoint(tmp_path, api_key_header):
    from httpx import ASGITransport, AsyncClient
    from app.main import app as backend_app

    file_path = tmp_path / "factura_apikey.csv"
    file_path.write_bytes(
        (
            "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
            "INV-2024-8888;2024-05-16;Beta Retail SA;A12345678;2500,50;3025,60\n"
        ).encode("utf-8")
    )

    async with AsyncClient(
        transport=ASGITransport(app=backend_app), base_url="http://test"
    ) as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": (file_path.name, f, "text/csv")},
                headers=api_key_header,
            )
        assert response.status_code == 202, response.text
        body = response.json()
        assert body["status"] == "pending"

        listing = await client.get("/api/v1/documents", headers=api_key_header)
        assert listing.status_code == 200, listing.text
        assert any(d["document_id"] == body["document_id"] for d in listing.json())