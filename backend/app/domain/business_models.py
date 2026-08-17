"""Domain models and Pydantic schemas for Specialized Business Engines (3-Way Matching, Norma 43, Payroll)."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MatchStatus(str, Enum):
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class MatchLineItemInput(BaseModel):
    sku: Optional[str] = None
    description: str
    ordered_qty: float = 0.0
    received_qty: float = 0.0
    invoiced_qty: float = 0.0
    po_unit_price: float = 0.0
    invoice_unit_price: float = 0.0


class MatchLineFinding(BaseModel):
    sku: Optional[str] = None
    description: str
    qty_discrepancy: float = 0.0
    price_discrepancy: float = 0.0
    line_variance: float = 0.0
    status: MatchStatus = MatchStatus.APPROVED
    message: str


class ThreeWayMatchRequest(BaseModel):
    po_number: str
    invoice_number: str
    gr_number: Optional[str] = None
    lines: List[MatchLineItemInput] = Field(default_factory=list)
    qty_tolerance_pct: float = 1.0  # 1% tolerance
    price_tolerance_pct: float = 0.5  # 0.5% tolerance


class ThreeWayMatchResult(BaseModel):
    status: MatchStatus
    po_number: str
    invoice_number: str
    total_po_amount: float
    total_invoice_amount: float
    total_variance_amount: float
    is_payable: bool
    findings: List[MatchLineFinding] = Field(default_factory=list)
    summary: str


class BankMovementLine(BaseModel):
    operation_date: str
    value_date: str
    common_concept: str
    own_concept: Optional[str] = None
    debit_or_credit: str = "C"  # "C" = Credit (Ingreso), "D" = Debit (Cargo)
    amount: float
    document_number: Optional[str] = None
    extended_concept: Optional[str] = None


class Norma43ParseResult(BaseModel):
    bank_code: str
    branch_code: str
    account_number: str
    currency: str = "EUR"
    initial_balance: float
    final_balance: float
    total_debit_amount: float
    total_credit_amount: float
    movements_count: int
    movements: List[BankMovementLine] = Field(default_factory=list)


class SplitEmployeeRecord(BaseModel):
    page_number: int
    employee_name: Optional[str] = None
    employee_nif: Optional[str] = None
    net_salary: Optional[float] = None
    output_filename: str


class PayrollSplitRequest(BaseModel):
    pdf_path: str
    output_directory: Optional[str] = None


class PayrollSplitResult(BaseModel):
    total_pages: int
    employees_detected: int
    splits: List[SplitEmployeeRecord] = Field(default_factory=list)
