"""Unit tests for the AEAT SII XML Generator."""

import pytest
from app.domain.compliance_models import SIIRegistrationRequest, TaxBreakdownItem
from app.services.compliance.sii_generator import SIIGenerator


def test_sii_generator_issued_invoice():
    generator = SIIGenerator()
    req = SIIRegistrationRequest(
        fiscal_year=2024,
        period="05",
        is_issued=True,
        emitter_nif="B12345678",
        emitter_name="Empresa Emisora S.L.",
        counterparty_nif="A87654321",
        counterparty_name="Cliente Destino S.A.",
        invoice_number="FAC-2024-001",
        invoice_date="2024-05-15",
        total_amount=1210.00,
        tax_breakdown=[
            TaxBreakdownItem(tax_rate_pct=21.0, taxable_base=1000.00, tax_quota=210.00)
        ],
    )

    result = generator.generate_sii_xml(req)

    assert result.is_valid is True
    assert "SuministroLRFacturasEmitidas" in result.xml_content
    assert "<sii:NIF>B12345678</sii:NIF>" in result.xml_content
    assert "<sii:NumSerieFacturaEmisor>FAC-2024-001</sii:NumSerieFacturaEmisor>" in result.xml_content
    assert "<sii:ImporteTotal>1210.00</sii:ImporteTotal>" in result.xml_content
    assert "<sii:TipoImpositivo>21.00</sii:TipoImpositivo>" in result.xml_content
