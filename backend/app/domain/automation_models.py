"""Domain models and Pydantic schemas for business automation rules and outgoing webhooks."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class RuleEventEnum(str, Enum):
    EXTRACTION_COMPLETED = "extraction_completed"
    NORMALIZATION_COMPLETED = "normalization_completed"


class RuleOperatorEnum(str, Enum):
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"
    CONTAINS = "contains"
    IS_EMPTY = "is_empty"
    NOT_EMPTY = "not_empty"


class AutomationRuleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    document_type: Optional[str] = Field(None, description="Filtro opcional por tipo de documento")
    event: RuleEventEnum = RuleEventEnum.EXTRACTION_COMPLETED
    field: str = Field(..., min_length=1, max_length=255)
    operator: RuleOperatorEnum
    value: Optional[Any] = None
    webhook_ids: List[str] = Field(
        default_factory=list,
        description="Webhooks destino; vacío = todos los webhooks activos de la organización",
    )
    enabled: bool = True


class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    document_type: Optional[str] = None
    event: Optional[RuleEventEnum] = None
    field: Optional[str] = Field(None, min_length=1, max_length=255)
    operator: Optional[RuleOperatorEnum] = None
    value: Optional[Any] = None
    webhook_ids: Optional[List[str]] = None
    enabled: Optional[bool] = None


class AutomationRuleResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    document_type: Optional[str] = None
    event: str
    field: str
    operator: str
    value: Optional[Any] = None
    webhook_ids: List[str] = Field(default_factory=list)
    enabled: bool
    created_at: str
    updated_at: str


class WebhookConfigCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    url: HttpUrl = Field(..., description="URL destino del webhook (ERP, Zapier, Make, n8n...)")
    secret: Optional[str] = Field(None, max_length=500, description="Clave HMAC opcional para firmar el payload")
    headers: Dict[str, str] = Field(default_factory=dict)
    active: bool = True


class WebhookConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    url: Optional[HttpUrl] = None
    secret: Optional[str] = Field(None, max_length=500)
    headers: Optional[Dict[str, str]] = None
    active: Optional[bool] = None


class WebhookConfigResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    url: str
    has_secret: bool
    headers: Dict[str, str] = Field(default_factory=dict)
    active: bool
    created_at: str
    updated_at: str


class WebhookDeliveryResponse(BaseModel):
    id: str
    organization_id: str
    webhook_id: Optional[str] = None
    rule_id: Optional[str] = None
    document_id: Optional[str] = None
    event: str
    url: str
    status: str
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    duration_ms: float
    created_at: str


class RuleEvaluationRequest(BaseModel):
    document_id: str
    table_index: int = Field(default=0, ge=0)


class RuleEvaluationResponse(BaseModel):
    rule_id: str
    rule_name: str
    matched: bool
    matched_value: Optional[Any] = None
    matched_rows: int = 0


class WebhookTestResponse(BaseModel):
    webhook_id: str
    webhook_name: str
    status: str
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    duration_ms: float