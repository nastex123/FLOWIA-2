"""Tests for RuleExtractor (Regex patterns & rapidfuzz header matching)."""

import pytest
from app.services.extractors.rule_extractor import RuleExtractor


def test_rule_extractor_regex_fields(sample_invoice_text):
    extractor = RuleExtractor()
    fields = extractor.extract_from_text(sample_invoice_text)

    # Validate email extraction
    assert "email" in fields
    assert fields["email"].value == "facturacion@suministros.com"

    # Validate tax ID extraction
    assert "tax_id" in fields
    assert fields["tax_id"].value in ("B87654321", "A11223344")

    # Validate invoice number
    assert "invoice_number" in fields
    assert "F-2024-0899" in fields["invoice_number"].value

    # Validate IBAN
    assert "iban" in fields
    assert fields["iban"].value == "ES7621000418401234567891"

    # Validate total amount normalization
    assert "total_amount" in fields
    assert fields["total_amount"].value == 1210.0


def test_fuzzy_header_matching():
    extractor = RuleExtractor()

    # Test variations of invoice_number
    assert extractor.match_canonical_field("Nº Factura") == "invoice_number"
    assert extractor.match_canonical_field("num_factura") == "invoice_number"
    assert extractor.match_canonical_field("Invoice Number") == "invoice_number"

    # Test variations of dates
    assert extractor.match_canonical_field("Fecha Emisión") == "issue_date"
    assert extractor.match_canonical_field("date") == "issue_date"
    assert extractor.match_canonical_field("f_vencimiento") == "due_date"

    # Test variations of totals
    assert extractor.match_canonical_field("Total a Pagar") == "total_amount"
    assert extractor.match_canonical_field("Importe Total (€)") == "total_amount"
    assert extractor.match_canonical_field("Base Imponible") == "subtotal"

    # Test unmatched garbage header
    assert extractor.match_canonical_field("xyz_unrelated_column_123", score_cutoff=85.0) is None
