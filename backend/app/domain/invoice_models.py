"""Domain models and Pydantic schemas for structured invoice processing."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    """Structured line item extracted from an invoice."""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    discount_pct: Optional[float] = None
    tax_rate_pct: Optional[float] = None
    line_total: Optional[float] = None


class TaxBreakdownItem(BaseModel):
    """Tax breakdown group by rate."""
    tax_rate_pct: float
    taxable_base: float
    tax_quota: float


class StructuredInvoice(BaseModel):
    """Canonical representation of a structured business invoice."""
    document_id: str
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: str = "EUR"
    items: List[InvoiceLineItem] = Field(default_factory=list)
    tax_breakdown: List[TaxBreakdownItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    total_amount: Optional[float] = None
    withholding_amount: Optional[float] = None
    shipping_amount: Optional[float] = None


class DocumentCheckDTO(BaseModel):
    """DTO for visual invoice check finding."""
    id: str
    organization_id: str
    document_id: str
    check_type: str
    severity: str
    status: str
    title: str
    detail_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
