"""Unit tests for the Veri*factu / TicketBAI hash chaining engine."""

import pytest
from app.domain.compliance_models import VerifactuChainingRequest
from app.services.compliance.verifactu_engine import VerifactuEngine


def test_verifactu_hash_chaining():
    engine = VerifactuEngine()

    # Invoice 1 (Genesis)
    req1 = VerifactuChainingRequest(
        issuer_nif="ESB12345678",
        invoice_series_number="F24-001",
        issue_date="2024-06-01",
        total_tax_quota=210.00,
        total_amount=1210.00,
        timestamp_iso="2024-06-01T10:00:00Z",
    )

    res1 = engine.compute_chained_hash(req1)
    assert len(res1.current_hash) == 64
    assert res1.previous_hash == engine.GENESIS_HASH
    assert "sede.agenciatributaria.gob.es" in res1.qr_payload_url
    assert "nif=ESB12345678" in res1.qr_payload_url

    # Invoice 2 (Chained to Invoice 1)
    req2 = VerifactuChainingRequest(
        issuer_nif="ESB12345678",
        invoice_series_number="F24-002",
        issue_date="2024-06-02",
        total_tax_quota=420.00,
        total_amount=2420.00,
        timestamp_iso="2024-06-02T11:00:00Z",
        previous_invoice_hash=res1.current_hash,
    )

    res2 = engine.compute_chained_hash(req2)
    assert len(res2.current_hash) == 64
    assert res2.previous_hash == res1.current_hash
    assert res2.current_hash != res1.current_hash
