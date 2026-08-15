"""Domain data models and Pydantic schemas for FlowMind AI."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Recognized business document types."""
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    PAYROLL = "payroll"
    INVENTORY = "inventory"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    FINANCIAL_REPORT = "financial_report"
    UNKNOWN = "unknown"


class ExtractedField(BaseModel):
    """Represents an atomic extracted data point with its provenance."""
    key: str = Field(..., description="Canonical key name")
    value: Any = Field(..., description="Extracted and normalized value")
    raw_value: Optional[str] = Field(None, description="Original unparsed string")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    extractor_type: str = Field(..., description="Extractor mechanism (regex, fuzzy, heuristic)")
    source_location: Optional[str] = Field(None, description="Page number, sheet name or cell coordinate")


class ExtractedTable(BaseModel):
    """Represents a structured table extracted from a spreadsheet or PDF."""
    sheet_or_page: str = Field(..., description="Identifier of the source sheet or page")
    headers: List[str] = Field(default_factory=list)
    rows_count: int = Field(default=0)
    records: List[Dict[str, Any]] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    """Result of categorizing a document with rules or ML."""
    document_type: DocumentType = DocumentType.UNKNOWN
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    classifier_type: str = Field(default="rule_based")
    matched_features: List[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Unified structured output for a processed document."""
    document_id: Optional[str] = None
    filename: str
    classification: ClassificationResult
    fields: Dict[str, ExtractedField] = Field(default_factory=dict)
    tables: List[ExtractedTable] = Field(default_factory=list)
    raw_text_summary: Optional[str] = None
    processing_time_ms: float = 0.0
