"""Tests for FlowMind Sentinel fraud and anomaly detection engine."""

import pytest
from app.domain.decision_models import SentinelAlertType, SentinelRiskLevel
from app.services.decision.sentinel import FlowMindSentinel


def test_sentinel_detects_bank_account_change():
    sentinel = FlowMindSentinel()
    vendor_tax_id = "ESB12345678"
    known_ibans = ["ES9121000418450200051332"]
    suspicious_new_iban = "ES6000491500051234567892"

    alert = sentinel.check_bank_account_change(
        vendor_tax_id=vendor_tax_id,
        current_iban=suspicious_new_iban,
        known_vendor_ibans=known_ibans,
    )

    assert alert is not None
    assert alert.alert_type == SentinelAlertType.BANK_ACCOUNT_CHANGE
    assert alert.risk_level == SentinelRiskLevel.CRITICAL
    assert "Cambio no verificado" in alert.title


def test_sentinel_ignores_known_bank_account():
    sentinel = FlowMindSentinel()
    vendor_tax_id = "ESB12345678"
    known_ibans = ["ES91 2100 0418 4502 0005 1332"]
    legit_iban = "ES9121000418450200051332"

    alert = sentinel.check_bank_account_change(
        vendor_tax_id=vendor_tax_id,
        current_iban=legit_iban,
        known_vendor_ibans=known_ibans,
    )

    assert alert is None


def test_sentinel_detects_exact_duplicate_invoice():
    sentinel = FlowMindSentinel()
    historical = [
        {
            "document_id": "doc-hist-001",
            "vendor_tax_id": "ESB12345678",
            "invoice_number": "FAC-2024-001",
            "invoice_date": "2024-06-01",
            "total_amount": 1250.00,
        }
    ]

    alert = sentinel.check_duplicate(
        document_id="doc-new-002",
        vendor_tax_id="ESB12345678",
        invoice_number="FAC-2024-001",
        invoice_date="2024-06-01",
        total_amount=1250.00,
        historical_records=historical,
    )

    assert alert is not None
    assert alert.alert_type == SentinelAlertType.MULTIDIMENSIONAL_DUPLICATE
    assert alert.risk_level == SentinelRiskLevel.HIGH
    assert "Factura Duplicada Detectada" in alert.title


def test_sentinel_detects_threshold_avoidance():
    sentinel = FlowMindSentinel(approval_threshold=10000.0)
    # Threshold is 10k. Range 9.5k to 10k
    recent_amounts = [9800.0, 9950.0]
    current_amount = 9900.0

    alert = sentinel.check_threshold_avoidance(
        current_amount=current_amount,
        recent_amounts=recent_amounts,
        margin_pct=0.05,
        min_occurrences=3,
    )

    assert alert is not None
    assert alert.alert_type == SentinelAlertType.THRESHOLD_AVOIDANCE
    assert alert.risk_level == SentinelRiskLevel.MEDIUM


def test_sentinel_comprehensive_audit():
    sentinel = FlowMindSentinel(approval_threshold=10000.0)
    vendor_tax_id = "ESB12345678"
    known_ibans = ["ES9121000418450200051332"]

    res = sentinel.audit_document(
        document_id="doc-999",
        vendor_tax_id=vendor_tax_id,
        invoice_number="F-2024-999",
        invoice_date="2024-06-15",
        total_amount=9850.0,
        iban="ES0000000000000000000000",  # Fraudulent IBAN
        known_vendor_ibans=known_ibans,
        recent_amounts=[9800.0, 9900.0],
    )

    assert res.total_alerts >= 1
    assert res.highest_risk == SentinelRiskLevel.CRITICAL
    assert res.risk_score == 1.0
