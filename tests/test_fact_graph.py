"""Tests for the Fact Graph Engine."""

import pytest
from app.services.decision.fact_graph import FactGraphEngine


def test_fact_graph_overbilling_detection():
    graph_engine = FactGraphEngine()

    # 1. Add vendor and Project
    graph_engine.add_project(project_id="proj-1", name="Construcción Nave Norte", budget=50000.0)
    graph_engine.add_vendor(vendor_id="vend-1", name="Acme S.L.", tax_id="ESB12345678")

    # 2. Add PO for 10,000€
    graph_engine.add_purchase_order(
        po_id="po-100",
        po_number="PO-2024-100",
        vendor_id="vend-1",
        total_amount=10000.0,
        project_id="proj-1",
    )

    # 3. Add first invoice for 6,000€
    graph_engine.add_invoice(
        invoice_id="inv-1",
        invoice_number="FAC-001",
        vendor_id="vend-1",
        po_id="po-100",
        total_amount=6000.0,
    )

    # Check cumulative invoiced: 6000€ <= 10000€ -> Not overbilled
    check_1 = graph_engine.check_overbilling("po-100")
    assert check_1["is_overbilled"] is False
    assert check_1["total_invoiced"] == 6000.0

    # 4. Add second invoice for 5,500€ (Cumulative 11,500€ > 10,000€ PO budget)
    graph_engine.add_invoice(
        invoice_id="inv-2",
        invoice_number="FAC-002",
        vendor_id="vend-1",
        po_id="po-100",
        total_amount=5500.0,
    )

    check_2 = graph_engine.check_overbilling("po-100")
    assert check_2["is_overbilled"] is True
    assert check_2["total_invoiced"] == 11500.0
    assert check_2["overbilled_amount"] == 1500.0


def test_fact_graph_orphan_invoices():
    graph_engine = FactGraphEngine()
    graph_engine.add_vendor(vendor_id="vend-1", name="Acme S.L.", tax_id="ESB12345678")

    # Invoice without PO
    graph_engine.add_invoice(
        invoice_id="inv-orphan",
        invoice_number="FAC-ORPHAN-01",
        vendor_id="vend-1",
        total_amount=3000.0,
        po_id=None,
    )

    orphans = graph_engine.find_orphan_invoices()
    assert "inv-orphan" in orphans


def test_fact_graph_project_summary():
    graph_engine = FactGraphEngine()
    graph_engine.add_project(project_id="proj-alpha", name="Proyecto Alpha", budget=100000.0)
    graph_engine.add_vendor(vendor_id="vend-1", name="Acme S.L.", tax_id="ESB12345678")

    graph_engine.add_purchase_order(
        po_id="po-1",
        po_number="PO-01",
        vendor_id="vend-1",
        total_amount=40000.0,
        project_id="proj-alpha",
    )

    graph_engine.add_invoice(
        invoice_id="inv-1",
        invoice_number="FAC-01",
        vendor_id="vend-1",
        po_id="po-1",
        total_amount=25000.0,
    )

    graph_engine.add_payment(
        payment_id="pay-1",
        invoice_id="inv-1",
        amount=25000.0,
        paid_at="2024-06-20",
    )

    summary = graph_engine.get_project_summary("proj-alpha")
    assert summary["budget"] == 100000.0
    assert summary["committed_po_total"] == 40000.0
    assert summary["invoiced_total"] == 25000.0
    assert summary["paid_total"] == 25000.0
    assert summary["remaining_budget"] == 60000.0
