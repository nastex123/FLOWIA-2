"""PDF extractor using PyMuPDF (fitz) for fast text extraction and pdfplumber for table parsing."""

import io
import time
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from app.core.exceptions import ExtractionError
from app.domain.schemas import (
    ClassificationResult,
    DocumentType,
    ExtractedField,
    ExtractedTable,
    ExtractionResult,
)
from app.services.extractors.base import BaseExtractor
from app.services.extractors.rule_extractor import RuleExtractor


class PDFExtractor(BaseExtractor):
    """Extracts text, metadata and structured tables from PDF files."""

    def __init__(self, rule_extractor: Optional[RuleExtractor] = None):
        self.rule_extractor = rule_extractor or RuleExtractor()

    def extract(
        self,
        file_input: Union[str, Path, bytes, BinaryIO],
        filename: str,
        document_id: Optional[str] = None,
        **kwargs,
    ) -> ExtractionResult:
        start_time = time.perf_counter()
        content_bytes = self._read_bytes(file_input)

        if not content_bytes.startswith(b"%PDF-"):
            raise ExtractionError(f"File '{filename}' is not a valid PDF document (missing %PDF- header).")

        raw_text_parts: List[str] = []
        tables: List[ExtractedTable] = []

        try:
            # 1. Extract text and pages with PyMuPDF (fitz)
            if fitz is not None:
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text("text")
                    if text:
                        raw_text_parts.append(text)
                doc.close()
            elif pdfplumber is not None:
                with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            raw_text_parts.append(text)
        except Exception as e:
            raise ExtractionError(f"Error reading PDF text from '{filename}': {str(e)}") from e

        # 2. Extract tables with pdfplumber
        if pdfplumber is not None:
            try:
                with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                    for i, page in enumerate(pdf.pages):
                        extracted_page_tables = page.extract_tables()
                        for t_idx, raw_table in enumerate(extracted_page_tables):
                            if not raw_table or len(raw_table) < 2:
                                continue
                            table = self._format_pdfplumber_table(raw_table, page_num=i + 1, table_index=t_idx + 1)
                            if table.rows_count > 0:
                                tables.append(table)
            except Exception as e:
                # Table extraction error shouldn't fail whole text parsing, but log as note
                pass

        full_text = "\n".join(raw_text_parts)

        # 3. Extract fields with rules from full text
        fields = self.rule_extractor.extract_from_text(full_text)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ExtractionResult(
            document_id=document_id,
            filename=filename,
            classification=ClassificationResult(
                document_type=self._guess_document_type(full_text, fields),
                confidence=0.85 if fields else 0.5,
                classifier_type="pdf_heuristics",
            ),
            fields=fields,
            tables=tables,
            raw_text_summary=full_text[:600] if full_text else None,
            processing_time_ms=round(elapsed_ms, 2),
        )

    def _format_pdfplumber_table(self, raw_table: List[List[Optional[str]]], page_num: int, table_index: int) -> ExtractedTable:
        """Converts raw list of lists from pdfplumber into an ExtractedTable model."""
        headers = [
            str(col).strip() if col is not None and str(col).strip() != "" else f"Column_{j}"
            for j, col in enumerate(raw_table[0])
        ]
        
        records: List[Dict[str, Any]] = []
        for row in raw_table[1:]:
            row_dict = {}
            for j, header in enumerate(headers):
                cell_val = row[j] if j < len(row) and row[j] is not None else ""
                row_dict[header] = str(cell_val).strip()
            records.append(row_dict)

        return ExtractedTable(
            sheet_or_page=f"Page {page_num} Table {table_index}",
            headers=headers,
            rows_count=len(records),
            records=records,
        )

    def _read_bytes(self, file_input: Union[str, Path, bytes, BinaryIO]) -> bytes:
        if isinstance(file_input, bytes):
            return file_input
        if isinstance(file_input, (str, Path)):
            with open(file_input, "rb") as f:
                return f.read()
        if hasattr(file_input, "read"):
            return file_input.read()
        raise ValueError(f"Invalid file_input type: {type(file_input)}")

    def _guess_document_type(self, text: str, fields: Dict[str, ExtractedField]) -> DocumentType:
        lower_text = text.lower()
        if "invoice_number" in fields or any(w in lower_text for w in ["factura", "invoice", "cif:", "nif:"]):
            return DocumentType.INVOICE
        if any(w in lower_text for w in ["nómina", "nomina", "devengos", "irpf", "seguridad social", "payroll"]):
            return DocumentType.PAYROLL
        if any(w in lower_text for w in ["pedido", "orden de compra", "purchase order", "po number"]):
            return DocumentType.PURCHASE_ORDER
        if any(w in lower_text for w in ["contrato", "cláusula", "acuerdo", "contract", "agreement"]):
            return DocumentType.CONTRACT
        if any(w in lower_text for w in ["balance", "cuenta de pérdidas y ganancias", "informe financiero", "financial report"]):
            return DocumentType.FINANCIAL_REPORT
        return DocumentType.UNKNOWN
