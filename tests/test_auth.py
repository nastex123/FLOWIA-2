"""Tests for JWT authentication, API keys and multi-tenant RBAC."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.infrastructure.database import async_session_factory, init_db
from app.infrastructure.models import User, UserRole


@pytest.mark.asyncio
async def test_register_login_and_me(auth_client):
    # 1. Register a new user with a new organization
    reg = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "nuevo@empresa.com",
            "password": "password123",
            "name": "Nuevo Usuario",
            "organization_name": "Empresa Nueva SL",
        },
    )
    assert reg.status_code == 201
    reg_data = reg.json()
    assert reg_data["access_token"]
    assert reg_data["user"]["email"] == "nuevo@empresa.com"
    assert reg_data["user"]["role"] == UserRole.ADMIN.value

    # 2. Login with those credentials
    login = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "nuevo@empresa.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    # 3. Wrong password must be rejected
    bad = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "nuevo@empresa.com", "password": "incorrecta"},
    )
    assert bad.status_code == 401

    # 4. /me returns default org + memberships
    me = await auth_client.get("/api/v1/auth/me")
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["default_organization"]["id"] == settings.DEFAULT_ADMIN_ORG
    assert any(o["id"] == settings.DEFAULT_ADMIN_ORG for o in me_data["organizations"])


@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/documents")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_api_key_creation_and_ingestion(auth_client, sample_csv_invoice):
    # 1. Create an API key (plaintext returned once)
    create = await auth_client.post(
        "/api/v1/auth/api-keys", json={"name": "Integración ERP"}
    )
    assert create.status_code == 201
    key_data = create.json()
    api_key = key_data["key"]
    assert api_key.startswith(settings.API_KEY_PREFIX)
    key_id = key_data["id"]

    # 2. List shows only the masked prefix, never the full key
    listed = await auth_client.get("/api/v1/auth/api-keys")
    assert listed.status_code == 200
    assert any(k["id"] == key_id and k["prefix"] == key_data["prefix"] for k in listed.json())

    # 3. Use the API key for unattended upload
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"file": ("auto_batch.csv", sample_csv_invoice, "text/csv")}
        resp = await ac.post(
            "/api/v1/documents/upload",
            files=files,
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 202

        # 4. Revoke the key and confirm uploads are rejected
        revoked = await auth_client.delete(f"/api/v1/auth/api-keys/{key_id}")
        assert revoked.status_code == 200
        resp2 = await ac.post(
            "/api/v1/documents/upload",
            files={"file": ("auto_batch_2.csv", sample_csv_invoice, "text/csv")},
            headers={"X-API-Key": api_key},
        )
        assert resp2.status_code == 401


@pytest.mark.asyncio
async def test_multi_tenant_isolation(auth_client, sample_csv_invoice):
    # Register two different organizations
    org_a = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "orga@test.com", "password": "password123", "organization_name": "Org A"},
    )
    org_b = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "orgb@test.com", "password": "password123", "organization_name": "Org B"},
    )
    token_a = org_a.json()["access_token"]
    token_b = org_b.json()["access_token"]

    transport = ASGITransport(app=app)

    # Upload a document in Org A
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers_a = {"Authorization": f"Bearer {token_a}"}
        files = {"file": ("orga_file.csv", sample_csv_invoice, "text/csv")}
        up = await ac.post("/api/v1/documents/upload", files=files, headers=headers_a)
        assert up.status_code == 202
        doc_id = up.json()["document_id"]

        # Org A can read it
        ok = await ac.get(f"/api/v1/documents/{doc_id}", headers=headers_a)
        assert ok.status_code == 200

        # Org B cannot read it (404, not leak)
        headers_b = {"Authorization": f"Bearer {token_b}"}
        denied = await ac.get(f"/api/v1/documents/{doc_id}", headers=headers_b)
        assert denied.status_code == 404


@pytest.mark.asyncio
async def test_rbac_viewer_cannot_create_schemas(auth_client):
    # Create a member user
    reg = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "member@test.com", "password": "password123", "organization_name": "Org RBAC"},
    )
    token = reg.json()["access_token"]

    # Downgrade that user to Viewer directly in the DB
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == "member@test.com"))
        user = result.scalar_one()
        user.role = UserRole.VIEWER
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "name": "No Permitido",
            "document_type": "custom",
            "fields": [{"name": "x", "label": "X", "data_type": "string"}],
        }
        resp = await ac.post("/api/v1/schemas", json=payload, headers=headers)
        assert resp.status_code == 403