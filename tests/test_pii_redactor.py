"""Unit tests for the Local PII & GDPR Redactor."""

import pytest
from app.domain.compliance_models import PIIRedactionRequest
from app.services.compliance.pii_redactor import PIIRedactor


def test_pii_redactor_masks_sensitive_data():
    redactor = PIIRedactor()
    raw_text = (
        "El empleado Juan Pérez con DNI 12345678Z y teléfono +34 612 345 678 "
        "solicita el abono a la cuenta ES9121000418450200051332. "
        "Contacto: juan.perez@empresa.com"
    )

    req = PIIRedactionRequest(text=raw_text)
    res = redactor.redact(req)

    assert res.total_redactions >= 4
    assert "[REDACTED_NIF]" in res.sanitized_text
    assert "[REDACTED_IBAN]" in res.sanitized_text
    assert "[REDACTED_EMAIL]" in res.sanitized_text
    assert "[REDACTED_PHONE]" in res.sanitized_text
    assert "12345678Z" not in res.sanitized_text
    assert "ES9121000418450200051332" not in res.sanitized_text
    assert "juan.perez@empresa.com" not in res.sanitized_text
