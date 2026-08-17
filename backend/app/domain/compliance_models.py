"""Domain models and Pydantic schemas for Fiscal Compliance, Veri*factu, SII AEAT and PII Redaction."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvoiceFiscalType(str, Enum):
    F1 = "F1"  # Factura ordinaria
    F2 = "F2"  # Factura simplificada (ticket)
    R1 = "R1"  # Factura rectificativa


class TaxBreakdownItem(BaseModel):
    tax_rate_pct: float
    taxable_base: float
    tax_quota: float
    surcharge_pct: Optional[float] = None
    surcharge_quota: Optional[float] = None


class SIIRegistrationRequest(BaseModel):
    fiscal_year: int = 2024
    period: str = "01"  # "01".."12" or "1T".."4T"
    is_issued: bool = True  # True: Emitida, False: Recibida
    emitter_nif: str
    emitter_name: str
    counterparty_nif: str
    counterparty_name: str
    invoice_number: str
    invoice_date: str  # YYYY-MM-DD
    total_amount: float
    tax_breakdown: List[TaxBreakdownItem] = Field(default_factory=list)


class SIIRegistrationResult(BaseModel):
    is_valid: bool
    message_type: str
    xml_content: str
    fields_count: int


class VerifactuChainingRequest(BaseModel):
    issuer_nif: str
    invoice_series_number: str
    issue_date: str
    invoice_type: str = "F1"
    total_tax_quota: float
    total_amount: float
    timestamp_iso: Optional[str] = None
    previous_invoice_hash: Optional[str] = None


class VerifactuChainingResult(BaseModel):
    current_hash: str
    previous_hash: str
    qr_payload_url: str
    signature_summary: str


class PIIRedactionRequest(BaseModel):
    text: str
    mask_nif: bool = True
    mask_iban: bool = True
    mask_email: bool = True
    mask_phone: bool = True


class RedactedSpan(BaseModel):
    pii_type: str
    original_snippet: str
    start_pos: int
    end_pos: int


class PIIRedactionResult(BaseModel):
    sanitized_text: str
    total_redactions: int
    redactions: List[RedactedSpan] = Field(default_factory=list)
