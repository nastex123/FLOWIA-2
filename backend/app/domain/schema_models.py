"""Domain models and Pydantic schemas for custom business data schemas and column mappings."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


class FieldDefinition(BaseModel):
    name: str = Field(..., description="Canonical field identifier (e.g. unit_price)")
    label: str = Field(..., description="Human-readable label (e.g. Precio Unitario)")
    data_type: DataType = Field(default=DataType.STRING)
    required: bool = Field(default=False)
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list, description="Common column headers used for auto-matching")


class SchemaCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    document_type: str = Field(default="custom")
    fields: List[FieldDefinition] = Field(..., min_length=1)


class SchemaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[str] = None
    fields: Optional[List[FieldDefinition]] = None


class SchemaResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    document_type: str
    fields: List[FieldDefinition]
    created_at: str
    updated_at: str


class AutoMapSuggestion(BaseModel):
    target_field: str
    target_label: str
    data_type: DataType
    required: bool
    suggested_source_column: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class AutoMapResponse(BaseModel):
    schema_id: str
    schema_name: str
    available_source_columns: List[str]
    mappings: List[AutoMapSuggestion]


class NormalizeRequest(BaseModel):
    schema_id: str
    table_index: int = Field(default=0, ge=0)
    column_mapping: Dict[str, str] = Field(
        ...,
        description="Dictionary where key is target schema field name and value is source column name",
    )


class NormalizedDatasetResponse(BaseModel):
    schema_id: str
    schema_name: str
    total_records: int
    headers: List[str]
    records: List[Dict[str, Any]]
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)
