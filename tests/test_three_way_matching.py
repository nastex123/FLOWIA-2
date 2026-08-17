"""Unit tests for the 3-Way Matching Engine."""

import pytest
from app.domain.business_models import MatchLineItemInput, MatchStatus
from app.services.business.three_way_matching import ThreeWayMatchingEngine


def test_three_way_matching_exact_approval():
    engine = ThreeWayMatchingEngine()
    lines = [
        MatchLineItemInput(
            sku="MAT-001",
            description="Cemento Portland 25kg",
            ordered_qty=100.0,
            received_qty=100.0,
            invoiced_qty=100.0,
            po_unit_price=5.50,
            invoice_unit_price=5.50,
        )
    ]

    res = engine.reconcile(
        po_number="PO-2024-001",
        invoice_number="FAC-2024-001",
        lines=lines,
    )

    assert res.status == MatchStatus.APPROVED
    assert res.is_payable is True
    assert res.total_variance_amount == 0.0
    assert len(res.findings) == 1
    assert res.findings[0].status == MatchStatus.APPROVED


def test_three_way_matching_excess_quantity_rejected():
    engine = ThreeWayMatchingEngine()
    lines = [
        MatchLineItemInput(
            sku="MAT-002",
            description="Ladrillo Hueco Doble",
            ordered_qty=500.0,
            received_qty=500.0,
            invoiced_qty=600.0,  # 100 extra units invoiced (20% excess)
            po_unit_price=0.40,
            invoice_unit_price=0.40,
        )
    ]

    res = engine.reconcile(
        po_number="PO-2024-002",
        invoice_number="FAC-2024-002",
        lines=lines,
        qty_tolerance_pct=1.0,
    )

    assert res.status == MatchStatus.REJECTED
    assert res.is_payable is False
    assert res.findings[0].status == MatchStatus.REJECTED
    assert res.findings[0].qty_discrepancy == 100.0


def test_three_way_matching_price_inflation_rejected():
    engine = ThreeWayMatchingEngine()
    lines = [
        MatchLineItemInput(
            sku="SRV-001",
            description="Alquiler Grúa Torre",
            ordered_qty=1.0,
            received_qty=1.0,
            invoiced_qty=1.0,
            po_unit_price=1200.0,
            invoice_unit_price=1500.0,  # +300€ over agreed price
        )
    ]

    res = engine.reconcile(
        po_number="PO-2024-003",
        invoice_number="FAC-2024-003",
        lines=lines,
        price_tolerance_pct=0.5,
    )

    assert res.status == MatchStatus.REJECTED
    assert res.is_payable is False
    assert res.findings[0].price_discrepancy == 300.0
