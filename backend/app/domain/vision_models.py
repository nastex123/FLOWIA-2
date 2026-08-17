"""Domain models and Pydantic schemas for Computer Vision, Barcodes, QR and OCR."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BarcodeFormat(str, Enum):
    QR_CODE = "QR_CODE"
    DATA_MATRIX = "DATA_MATRIX"
    PDF_417 = "PDF_417"
    CODE_128 = "CODE_128"
    CODE_39 = "CODE_39"
    EAN_13 = "EAN_13"
    EAN_8 = "EAN_8"
    UPC_A = "UPC_A"
    UNKNOWN = "UNKNOWN"


class BarcodeItem(BaseModel):
    format: BarcodeFormat = BarcodeFormat.UNKNOWN
    raw_payload: str
    position_box: Optional[List[int]] = Field(None, description="[x, y, width, height]")
    parsed_type: Optional[str] = Field(None, description="e.g. ticketbai, verifactu, sepa_epc, key_value, plain_text")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckboxItem(BaseModel):
    checkbox_id: str
    position_box: List[int] = Field(..., description="[x, y, width, height]")
    is_checked: bool
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    fill_ratio: float = 0.0


class DewarpInfo(BaseModel):
    applied: bool = False
    original_dimensions: List[int] = Field(default_factory=list)
    warped_dimensions: List[int] = Field(default_factory=list)
    corners: Optional[List[List[int]]] = None


class VisionExtractionResult(BaseModel):
    barcodes: List[BarcodeItem] = Field(default_factory=list)
    checkboxes: List[CheckboxItem] = Field(default_factory=list)
    ocr_text: Optional[str] = None
    dewarp_info: Optional[DewarpInfo] = None
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
