"""Tests for business automation rules, outgoing webhooks and the audit trail."""

import pytest
import httpx
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.rules.rule_engine import (
    evaluate_field_rule,
    evaluate_records_rule,
    evaluate_rule_value,
    extract_field_value,
)


# ==========================================
# Rule engine unit tests
# ==========================================


def test_numeric_operators():
    assert evaluate_rule_value("gt", 100, 150) is True
    assert evaluate_rule_value("gt", 100, 50) is False
    assert evaluate_rule_value("lt", 100, 50) is True
    assert evaluate_rule_value("gte", 100, 100) is True
    assert evaluate_rule_value("lte", 100, 100) is True
    assert evaluate_rule_value("eq", 100, "100") is True
    assert evaluate_rule_value("neq", 100, 200) is True


def test_numeric_operators_with_european_decimals():
    assert evaluate_rule_value("gt", 1000, "1.210,00") is True
    assert evaluate_rule_value("lt", 2000, "1.210,00") is True
    assert evaluate_rule_value("gt", 2000, "1.210,00 €") is False


def test_string_operators():
    assert evaluate_rule_value("contains", "urgente", "PAGO URGENTE") is True
    assert evaluate_rule_value("contains", "nada", "Hola mundo") is False
    assert evaluate_rule_value("eq", "SI", "si") is True


def test_empty_operators():
    assert evaluate_rule_value("is_empty", None, None) is True
    assert evaluate_rule_value("is_empty", None, "") is True
    assert evaluate_rule_value("is_empty", None, "dato") is False
    assert evaluate_rule_value("not_empty", None, "dato") is True
    assert evaluate_rule_value("not_empty", None, "") is False


def test_rule_evaluation_helpers():
    rule = {"field": "total_amount", "operator": "gt", "value": 1000}
    assert evaluate_field_rule(rule, "1.210,00") is True

    records = [
        {"total_amount": 500.0},
        {"total_amount": 2500.0},
        {"total_amount": 3000.0},
    ]
    matched, first_value, count = evaluate_records_rule(rule, records)
    assert matched is True
    assert first_value == 2500.0
    assert count == 2

    fields = {"total_amount": {"value": "1.210,00", "confidence": 0.9}}
    assert extract_field_value(fields, "total_amount") == "1.210,00"


# ==========================================
# Rules & Webhooks API tests
# ==========================================


@pytest.mark.asyncio
async def test_rules_crud(auth_client):
    payload = {
        "name": "Alertar si total > 5000",
        "description": "Dispara aviso al superar el umbral",
        "document_type": "invoice",
        "event": "extraction_completed",
        "field": "total_amount",
        "operator": "gt",
        "value": 5000,
        "enabled": True,
    }
    create = await auth_client.post("/api/v1/rules", json=payload)
    assert create.status_code == 201
    rule_id = create.json()["id"]
    assert create.json()["operator"] == "gt"

    listed = await auth_client.get("/api/v1/rules")
    assert listed.status_code == 200
    assert any(r["id"] == rule_id for r in listed.json())

    fetched = await auth_client.get(f"/api/v1/rules/{rule_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Alertar si total > 5000"

    updated = await auth_client.put(
        f"/api/v1/rules/{rule_id}",
        json={"value": 8000, "enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json()["value"] == 8000
    assert updated.json()["enabled"] is False

    deleted = await auth_client.delete(f"/api/v1/rules/{rule_id}")
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_webhooks_crud_and_secret_masking(auth_client, monkeypatch):
    from app.services.webhooks import dispatcher as dispatcher_module

    async def fake_send(url, payload, headers, timeout):
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(dispatcher_module, "_send_request", fake_send)

    create = await auth_client.post(
        "/api/v1/webhooks",
        json={
            "name": "ERP Contabilidad",
            "url": "https://erp.example.com/flowmind/invoice",
            "secret": "clave-secreta",
            "headers": {"X-Tenant": "acme"},
        },
    )
    assert create.status_code == 201
    wh = create.json()
    wh_id = wh["id"]
    # The secret must never be returned
    assert wh["has_secret"] is True
    assert "secret" not in wh
    assert wh["headers"] == {"X-Tenant": "acme"}

    # Test ping
    test_resp = await auth_client.post(f"/api/v1/webhooks/{wh_id}/test")
    assert test_resp.status_code == 200
    assert test_resp.json()["status"] == "success"

    # Audit trail for this webhook
    deliveries = await auth_client.get(f"/api/v1/webhooks/{wh_id}/deliveries")
    assert deliveries.status_code == 200
    assert deliveries.json() != []

    # Update and delete
    upd = await auth_client.put(f"/api/v1/webhooks/{wh_id}", json={"active": False})
    assert upd.status_code == 200
    assert upd.json()["active"] is False

    deleted = await auth_client.delete(f"/api/v1/webhooks/{wh_id}")
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_pipeline_fires_rule_webhook_and_audit(
    auth_client, sample_csv_invoice, monkeypatch
):
    from app.services.webhooks import dispatcher as dispatcher_module

    captured: dict = {}

    async def fake_send(url, payload, headers, timeout):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(dispatcher_module, "_send_request", fake_send)

    # 1. Register a webhook
    wh_resp = await auth_client.post(
        "/api/v1/webhooks",
        json={"name": "Hook Automatización", "url": "https://hook.example.com/invoice", "secret": "abc"},
    )
    wh_id = wh_resp.json()["id"]

    # 2. Register a rule: alert when invoice total > 1000
    rule_resp = await auth_client.post(
        "/api/v1/rules",
        json={
            "name": "Alertar total > 1000",
            "document_type": "invoice",
            "event": "extraction_completed",
            "field": "total_amount",
            "operator": "gt",
            "value": 1000,
            "webhook_ids": [wh_id],
        },
    )
    rule_id = rule_resp.json()["id"]

    # 3. Upload an invoice CSV -> background pipeline processes it and fires the webhook
    files = {"file": ("invoice_auto.csv", sample_csv_invoice, "text/csv")}
    up_resp = await auth_client.post("/api/v1/documents/upload", files=files)
    assert up_resp.status_code == 202
    doc_id = up_resp.json()["document_id"]

    # 4. Webhook must have been dispatched with the right payload
    assert captured.get("url") == "https://hook.example.com/invoice"
    assert captured["payload"]["event"] == "extraction_completed"
    assert captured["payload"]["rule"]["name"] == "Alertar total > 1000"
    assert captured["payload"]["document"]["id"] == doc_id
    assert captured["headers"]["X-Webhook-Signature"].startswith("sha256=")

    # 5. Audit trail is persisted
    deliveries = await auth_client.get(f"/api/v1/webhooks/{wh_id}/deliveries")
    assert deliveries.status_code == 200
    delivery_list = deliveries.json()
    assert any(
        d["document_id"] == doc_id
        and d["rule_id"] == rule_id
        and d["status"] == "success"
        for d in delivery_list
    )

    # 6. Manual rule evaluation returns matched True
    eval_resp = await auth_client.post(
        f"/api/v1/rules/{rule_id}/evaluate",
        json={"document_id": doc_id},
    )
    assert eval_resp.status_code == 200
    assert eval_resp.json()["matched"] is True


@pytest.mark.asyncio
async def test_rule_not_matched_does_not_dispatch(
    auth_client, sample_csv_invoice, monkeypatch
):
    from app.services.webhooks import dispatcher as dispatcher_module

    dispatched: list = []

    async def fake_send(url, payload, headers, timeout):
        dispatched.append(payload)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(dispatcher_module, "_send_request", fake_send)

    await auth_client.post(
        "/api/v1/webhooks",
        json={"name": "Hook", "url": "https://hook.example.com/h"},
    )
    # Threshold far above the invoice total (max ~3025) -> never matches
    await auth_client.post(
        "/api/v1/rules",
        json={
            "name": "Umbral altísimo",
            "document_type": "invoice",
            "event": "extraction_completed",
            "field": "total_amount",
            "operator": "gt",
            "value": 100000,
        },
    )

    files = {"file": ("invoice_low.csv", sample_csv_invoice, "text/csv")}
    up_resp = await auth_client.post("/api/v1/documents/upload", files=files)
    assert up_resp.status_code == 202

    assert dispatched == []