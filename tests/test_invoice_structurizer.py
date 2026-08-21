"""Tests for the InvoiceStructurizer deterministic extraction engine."""

import pytest
from datetime import date
from app.services.invoice.structurizer import InvoiceStructurizer


@pytest.fixture
def structurizer():
    return InvoiceStructurizer()


def test_structurize_with_complete_fields_and_table(structurizer):
    extraction_data = {
        "fields": {
            "invoice_number": "INV-2024-001",
            "vendor_name": "Acme Supplies S.L.",
            "vendor_tax_id": "B12345678",
            "customer_name": "Global Services SA",
            "customer_tax_id": "A87654321",
            "issue_date": "2024-06-15",
            "due_date": "2024-07-15",
            "currency": "EUR",
            "subtotal": "1000.00",
            "tax_total": "210.00",
            "total_amount": "1210.00",
        },
        "tables": [
            {
                "headers": ["Descripción", "Cantidad", "Precio Unitario", "IVA %", "Total Línea"],
                "rows": [
                    ["Consultoría IT", "10", "80.00 €", "21%", "800.00 €"],
                    ["Licencia Software", "2", "100.00 €", "21%", "200.00 €"],
                ],
            }
        ],
    }

    result = structurizer.structurize(extraction_data, document_id="doc-123")

    assert result.document_id == "doc-123"
    assert result.invoice_number == "INV-2024-001"
    assert result.vendor_name == "Acme Supplies S.L."
    assert result.vendor_tax_id == "B12345678"
    assert result.customer_name == "Global Services SA"
    assert result.issue_date == date(2024, 6, 15)
    assert result.due_date == date(2024, 7, 15)
    assert result.currency == "EUR"
    assert result.subtotal == 1000.00
    assert result.tax_total == 210.00
    assert result.total_amount == 1210.00

    assert len(result.items) == 2
    assert result.items[0].description == "Consultoría IT"
    assert result.items[0].quantity == 10.0
    assert result.items[0].unit_price == 80.00
    assert result.items[0].line_total == 800.00
    assert result.items[0].tax_rate_pct == 21.0

    assert len(result.tax_breakdown) == 1
    assert result.tax_breakdown[0].tax_rate_pct == 21.0
    assert result.tax_breakdown[0].taxable_base == 1000.00
    assert result.tax_breakdown[0].tax_quota == 210.00


def test_structurize_header_only_invoice(structurizer):
    extraction_data = {
        "fields": {
            "num_factura": "F-9988",
            "proveedor": "Logística Rápida",
            "cif": "B99887766",
            "fecha": "2024-05-20",
            "base_imponible": "500,00",
            "cuota_iva": "105,00",
            "total": "605,00",
        },
        "tables": [],
    }

    result = structurizer.structurize(extraction_data, document_id="doc-456")

    assert result.invoice_number == "F-9988"
    assert result.vendor_name == "Logística Rápida"
    assert result.vendor_tax_id == "B99887766"
    assert result.issue_date == date(2024, 5, 20)
    assert result.subtotal == 500.00
    assert result.tax_total == 105.00
    assert result.total_amount == 605.00
    assert len(result.items) == 0
    assert len(result.tax_breakdown) == 1
    assert result.tax_breakdown[0].tax_rate_pct == 21.0
    assert result.tax_breakdown[0].taxable_base == 500.00
    assert result.tax_breakdown[0].tax_quota == 105.00


def test_structurize_multi_rate_tax_breakdown(structurizer):
    extraction_data = {
        "fields": {
            "invoice_number": "INV-MULTI",
        },
        "tables": [
            {
                "headers": ["Item", "Qty", "Price", "Tipo IVA", "Importe"],
                "rows": [
                    ["Libros (IVA superreducido)", "2", "50.00", "4", "100.00"],
                    ["Alimentos (IVA reducido)", "1", "100.00", "10", "100.00"],
                    ["Material de oficina (IVA general)", "1", "100.00", "21", "100.00"],
                ],
            }
        ],
    }

    result = structurizer.structurize(extraction_data, document_id="doc-789")

    assert result.subtotal == 300.00
    assert len(result.items) == 3
    assert len(result.tax_breakdown) == 3

    rates = {tb.tax_rate_pct: (tb.taxable_base, tb.tax_quota) for tb in result.tax_breakdown}
    assert rates[4.0] == (100.00, 4.00)
    assert rates[10.0] == (100.00, 10.00)
    assert rates[21.0] == (100.00, 21.00)
    assert result.tax_total == 35.00
    assert result.total_amount == 335.00  # Calculated subtotal (300) + tax (35)
