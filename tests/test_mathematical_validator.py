"""Tests for the Deterministic Mathematical Document Validator."""

import pytest
from app.domain.decision_models import DiscrepancySeverity, LineItemInput
from app.services.decision.mathematical_validator import MathematicalDocumentValidator


def test_mathematical_validator_exact_invoice():
    validator = MathematicalDocumentValidator()
    lines = [
        LineItemInput(description="Servidor ProLiant", quantity=2, unit_price=1000.0, discount_pct=10.0, tax_rate_pct=21.0),
        LineItemInput(description="Licencia SO", quantity=2, unit_price=200.0, discount_pct=0.0, tax_rate_pct=21.0),
    ]
    # Line 1: 2 * 1000 * 0.9 = 1800.00
    # Line 2: 2 * 200 = 400.00
    # Subtotal = 2200.00
    # Tax 21% = 462.00
    # Total = 2662.00

    res = validator.validate_invoice(
        lines=lines,
        document_subtotal=2200.00,
        document_tax=462.00,
        document_total=2662.00,
    )

    assert res.is_valid is True
    assert res.calculated_subtotal == 2200.00
    assert res.calculated_tax == 462.00
    assert res.calculated_total == 2662.00
    assert res.deviation == 0.0
    assert len(res.findings) == 0


def test_mathematical_validator_detects_total_error():
    validator = MathematicalDocumentValidator()
    lines = [
        LineItemInput(description="Material Construcción", quantity=10, unit_price=50.0, tax_rate_pct=21.0),
    ]
    # Subtotal = 500.00, Tax = 105.00, Expected Total = 605.00
    # Declared Total = 705.00 (100€ error)

    res = validator.validate_invoice(
        lines=lines,
        document_subtotal=500.00,
        document_tax=105.00,
        document_total=705.00,
    )

    assert res.is_valid is False
    assert res.deviation == 100.00
    assert len(res.findings) == 1
    assert res.findings[0].category == "total_check"
    assert res.findings[0].severity == DiscrepancySeverity.CRITICAL


def test_mathematical_validator_with_multiple_tax_groups_and_withholding():
    validator = MathematicalDocumentValidator()
    lines = [
        LineItemInput(description="Servicio Profesional", quantity=1, unit_price=1000.0, tax_rate_pct=21.0),
        LineItemInput(description="Libro Formativo", quantity=2, unit_price=50.0, tax_rate_pct=4.0),
    ]
    # Line 1: 1000.00 (Tax 21% = 210.00)
    # Line 2: 100.00 (Tax 4% = 4.00)
    # Subtotal = 1100.00
    # Tax = 214.00
    # Withholding (IRPF 15% on 1100) = 165.00
    # Shipping = 10.00
    # Total = 1100 + 214 - 165 + 10 = 1159.00

    res = validator.validate_invoice(
        lines=lines,
        document_subtotal=1100.00,
        document_tax=214.00,
        document_total=1159.00,
        withholding_pct=15.0,
        shipping_cost=10.00,
    )

    assert res.is_valid is True
    assert res.calculated_subtotal == 1100.00
    assert res.calculated_tax == 214.00
    assert res.calculated_total == 1159.00
    assert res.deviation == 0.0


def test_mathematical_validator_line_item_discrepancy():
    validator = MathematicalDocumentValidator()
    lines = [
        LineItemInput(
            description="Item erróneo",
            quantity=5,
            unit_price=10.0,
            discount_pct=0.0,
            tax_rate_pct=21.0,
            line_total=80.0,  # Expected 50.0
        )
    ]

    res = validator.validate_invoice(lines=lines, document_total=60.50)
    assert len(res.findings) >= 1
    assert any(f.category == "line_item_total" for f in res.findings)
