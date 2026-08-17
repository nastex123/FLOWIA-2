"""Domain models and Pydantic schemas for the Enterprise Decision Engine and Sentinel."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DiscrepancySeverity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class ValidationFinding(BaseModel):
    category: str = Field(..., description="E.g. line_item_sum, tax_calculation, total_check")
    severity: DiscrepancySeverity = DiscrepancySeverity.OK
    description: str
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    deviation: Optional[float] = None


class MathematicalValidationResult(BaseModel):
    is_valid: bool
    calculated_subtotal: float
    calculated_tax: float
    calculated_total: float
    document_total: Optional[float] = None
    deviation: float = 0.0
    findings: List[ValidationFinding] = Field(default_factory=list)


class EntityResolutionAction(str, Enum):
    AUTO_MERGE = "auto_merge"
    FLAG_FOR_REVIEW = "flag_for_review"
    CREATE_NEW = "create_new"


class EntityMatchResult(BaseModel):
    entity_id: Optional[str] = None
    canonical_name: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    action: EntityResolutionAction = EntityResolutionAction.CREATE_NEW
    matched_features: Dict[str, float] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)


class SentinelAlertType(str, Enum):
    BANK_ACCOUNT_CHANGE = "bank_account_change"
    MULTIDIMENSIONAL_DUPLICATE = "multidimensional_duplicate"
    THRESHOLD_AVOIDANCE = "threshold_avoidance"
    BENFORD_ANOMALY = "benford_anomaly"
    PRICE_SPIKE = "price_spike"
    SUSPICIOUS_ROUND_AMOUNT = "suspicious_round_amount"


class SentinelRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SentinelAlert(BaseModel):
    alert_type: SentinelAlertType
    risk_level: SentinelRiskLevel
    title: str
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: str


class SentinelAuditResult(BaseModel):
    total_alerts: int
    highest_risk: SentinelRiskLevel = SentinelRiskLevel.LOW
    alerts: List[SentinelAlert] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class DecisionScoreResult(BaseModel):
    decision_score: float = Field(default=1.0, ge=0.0, le=1.0)
    auto_approved: bool = False
    routing: str = "human_review"
    breakdown: Dict[str, float] = Field(default_factory=dict)
    summary: str


class LineItemInput(BaseModel):
    description: Optional[str] = None
    quantity: float = 1.0
    unit_price: float = 0.0
    discount_pct: float = 0.0
    tax_rate_pct: float = 21.0
    line_total: Optional[float] = None


class MathValidationRequest(BaseModel):
    document_id: Optional[str] = None
    lines: List[LineItemInput] = Field(default_factory=list)
    document_subtotal: Optional[float] = None
    document_tax: Optional[float] = None
    document_total: Optional[float] = None
    withholding_pct: float = 0.0
    shipping_cost: float = 0.0


class EntityResolveRequest(BaseModel):
    name: str
    tax_id: Optional[str] = None
    iban: Optional[str] = None
    email_domain: Optional[str] = None
    phone: Optional[str] = None


class SentinelAuditRequest(BaseModel):
    document_id: str
    vendor_tax_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    iban: Optional[str] = None
