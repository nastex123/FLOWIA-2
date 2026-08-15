"""Tabular extractor for Excel (XLSX, XLS) and CSV files."""

import csv
import io
import time
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union
import pandas as pd

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


class TabularExtractor(BaseExtractor):
    """Processes tabular spreadsheets and comma-separated files into structured records."""

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
        ext = Path(filename).suffix.lower()

        try:
            if ext in (".xlsx", ".xls"):
                tables, raw_text = self._parse_excel(file_input)
            elif ext in (".csv", ".tsv", ".txt"):
                tables, raw_text = self._parse_csv(file_input)
            else:
                raise ExtractionError(f"Unsupported tabular file extension: {ext}")
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            raise ExtractionError(f"Failed to process tabular file '{filename}': {str(e)}") from e

        # Extract fields from tabular headers and raw text
        fields: Dict[str, ExtractedField] = {}
        for table in tables:
            for header in table.headers:
                canonical_key = self.rule_extractor.match_canonical_field(header)
                if canonical_key and canonical_key not in fields and table.records:
                    # Sample first record value for this column
                    sample_val = table.records[0].get(header)
                    if sample_val is not None and str(sample_val).strip() != "":
                        fields[canonical_key] = ExtractedField(
                            key=canonical_key,
                            value=sample_val,
                            raw_value=str(sample_val),
                            confidence=0.90,
                            extractor_type="tabular_column_mapping",
                            source_location=f"{table.sheet_or_page}:{header}",
                        )

        # Fallback text regex search on extracted cell texts
        text_fields = self.rule_extractor.extract_from_text(raw_text)
        for k, v in text_fields.items():
            if k not in fields:
                fields[k] = v

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ExtractionResult(
            document_id=document_id,
            filename=filename,
            classification=ClassificationResult(
                document_type=self._guess_document_type(tables, fields),
                confidence=0.85 if fields else 0.5,
                classifier_type="tabular_heuristics",
            ),
            fields=fields,
            tables=tables,
            raw_text_summary=raw_text[:500] if raw_text else None,
            processing_time_ms=round(elapsed_ms, 2),
        )

    def _parse_csv(self, file_input: Union[str, Path, bytes, BinaryIO]) -> tuple[List[ExtractedTable], str]:
        """Detects delimiter and parses CSV content into ExtractedTable."""
        content_bytes = self._read_bytes(file_input)
        
        # Try UTF-8 first, fallback to latin-1
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("latin-1", errors="replace")

        # Sniff delimiter
        sample = text[:4096]
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","

        df = pd.read_csv(
            io.StringIO(text),
            sep=delimiter,
            dtype=str,
            keep_default_na=False,
            on_bad_lines="skip",
        )
        table = self._dataframe_to_extracted_table(df, sheet_name="CSV")
        return [table], text

    def _parse_excel(self, file_input: Union[str, Path, bytes, BinaryIO]) -> tuple[List[ExtractedTable], str]:
        """Parses all sheets of an Excel workbook."""
        content_bytes = self._read_bytes(file_input)
        excel_file = pd.ExcelFile(io.BytesIO(content_bytes))
        
        tables: List[ExtractedTable] = []
        raw_text_parts: List[str] = []

        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name=sheet_name, dtype=str, keep_default_na=False)
            table = self._dataframe_to_extracted_table(df, sheet_name=sheet_name)
            if table.rows_count > 0 or table.headers:
                tables.append(table)
                # Append sample text for heuristics
                headers_text = " ".join(table.headers)
                raw_text_parts.append(f"Sheet: {sheet_name} Headers: {headers_text}")

        return tables, "\n".join(raw_text_parts)

    def _dataframe_to_extracted_table(self, df: pd.DataFrame, sheet_name: str) -> ExtractedTable:
        """Converts a pandas DataFrame into a sanitized ExtractedTable."""
        # Drop completely empty rows and columns
        df = df.dropna(how="all").dropna(axis=1, how="all")
        
        # Clean column names (strip whitespace and handle unnamed)
        cleaned_columns = [
            f"Column_{i}" if str(col).startswith("Unnamed:") or not str(col).strip() else str(col).strip()
            for i, col in enumerate(df.columns)
        ]
        df.columns = cleaned_columns

        # Sanitize potential formula injections in cell values
        records: List[Dict[str, Any]] = []
        for row in df.to_dict(orient="records"):
            sanitized_row = {
                k: self._sanitize_cell(v) for k, v in row.items()
            }
            records.append(sanitized_row)

        return ExtractedTable(
            sheet_or_page=sheet_name,
            headers=cleaned_columns,
            rows_count=len(records),
            records=records,
        )

    def _sanitize_cell(self, value: Any) -> Any:
        """Sanitizes dangerous formula prefixes to prevent spreadsheet injection."""
        if isinstance(value, str):
            val = value.strip()
            if val.startswith(("=", "+", "-", "@", "\t", "\r")):
                return f"'{val}"
            return val
        return value

    def _read_bytes(self, file_input: Union[str, Path, bytes, BinaryIO]) -> bytes:
        """Helper to safely extract raw bytes from various input formats."""
        if isinstance(file_input, bytes):
            return file_input
        if isinstance(file_input, (str, Path)):
            with open(file_input, "rb") as f:
                return f.read()
        if hasattr(file_input, "read"):
            return file_input.read()
        raise ValueError(f"Invalid file_input type: {type(file_input)}")

    def _guess_document_type(self, tables: List[ExtractedTable], fields: Dict[str, ExtractedField]) -> DocumentType:
        """Heuristically guesses document type based on discovered fields & headers."""
        all_headers = set()
        for t in tables:
            all_headers.update([h.lower() for h in t.headers])

        if "invoice_number" in fields or any(k in all_headers for k in ["factura", "invoice", "iva", "nif", "cif"]):
            return DocumentType.INVOICE
        if any(k in all_headers for k in ["sku", "stock", "inventario", "cantidad", "almacen"]):
            return DocumentType.INVENTORY
        if any(k in all_headers for k in ["salario", "nomina", "payroll", "irpf", "bruto", "neto"]):
            return DocumentType.PAYROLL
        if any(k in all_headers for k in ["pedido", "purchase_order", "po_number", "orden"]):
            return DocumentType.PURCHASE_ORDER

        return DocumentType.UNKNOWN
