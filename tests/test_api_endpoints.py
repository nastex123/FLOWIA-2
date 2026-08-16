"""FastAPI endpoints integration tests using httpx AsyncClient."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ai_engine"] == "pure_libraries_local"


@pytest.mark.asyncio
async def test_upload_and_get_document(sample_csv_invoice, auth_client):
    # 1. Upload document (authenticated as default admin, org = default-org)
    files = {
        "file": ("invoice_batch_01.csv", sample_csv_invoice, "text/csv")
    }
    upload_resp = await auth_client.post("/api/v1/documents/upload", files=files)
    assert upload_resp.status_code == 202
    upload_data = upload_resp.json()
    doc_id = upload_data["document_id"]
    assert doc_id is not None
    assert upload_data["filename"] == "invoice_batch_01.csv"

    # 2. Get document details
    detail_resp = await auth_client.get(f"/api/v1/documents/{doc_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["document_id"] == doc_id
    assert detail_data["filename"] == "invoice_batch_01.csv"

    # 3. List documents for organization
    list_resp = await auth_client.get("/api/v1/documents")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert any(d["document_id"] == doc_id for d in list_data)
