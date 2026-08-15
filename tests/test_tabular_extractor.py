"""Tests for TabularExtractor (CSV, Excel parsing and security sanitization)."""

import pytest
from app.domain.schemas import DocumentType
from app.services.extractors.tabular_extractor import TabularExtractor


def test_csv_extraction_with_semicolon_delimiter(sample_csv_invoice):
    extractor = TabularExtractor()
    result = extractor.extract(
        file_input=sample_csv_invoice,
        filename="invoice_may_2024.csv",
    )

    assert result.filename == "invoice_may_2024.csv"
    assert len(result.tables) == 1
    table = result.tables[0]
    assert table.rows_count == 2
    assert "Factura_No" in table.headers
    assert "Total_Factura" in table.headers

    # Check fuzzy mapped fields
    assert "invoice_number" in result.fields
    assert result.fields["invoice_number"].value == "INV-2024-9988"

    # Check document classification
    assert result.classification.document_type == DocumentType.INVOICE


def test_csv_formula_injection_sanitization(sample_csv_with_formula_injection):
    extractor = TabularExtractor()
    result = extractor.extract(
        file_input=sample_csv_with_formula_injection,
        filename="security_test.csv",
    )

    table = result.tables[0]
    for row in table.records:
        payload = row.get("FormulaPayload", "")
        # Dangerous formula characters (=, +, @) must be prefixed with single quote
        assert payload.startswith("'") or not payload.startswith(("=", "+", "@"))
