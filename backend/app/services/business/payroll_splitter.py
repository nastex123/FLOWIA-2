"""Mega-PDF Payroll Splitter: Disaggregates mass payroll documents into per-employee PDFs."""

import re
from pathlib import Path
from typing import BinaryIO, List, Optional, Union

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from app.core.exceptions import ExtractionError
from app.domain.business_models import PayrollSplitResult, SplitEmployeeRecord
from app.services.extractors.rule_extractor import RuleExtractor


class PayrollSplitter:
    """Splits multi-page payroll PDFs into individual employee PDF documents."""

    def __init__(self, rule_extractor: Optional[RuleExtractor] = None):
        self.rule_extractor = rule_extractor or RuleExtractor()

    def split_payroll_pdf(
        self,
        pdf_input: Union[str, Path, bytes, BinaryIO],
        output_directory: Optional[Union[str, Path]] = None,
    ) -> PayrollSplitResult:
        if fitz is None:
            raise ExtractionError("PyMuPDF (fitz) is required for PDF payroll splitting.")

        raw_bytes = self._read_bytes(pdf_input)
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
        total_pages = len(doc)

        out_dir = Path(output_directory) if output_directory else Path.cwd() / "data" / "payroll_splits"
        out_dir.mkdir(parents=True, exist_ok=True)

        splits: List[SplitEmployeeRecord] = []

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_text = page.get_text("text")

            # Extract fields for this employee page
            fields = self.rule_extractor.extract_from_text(page_text)
            emp_nif = fields.get("vendor_tax_id", {}).get("value") if "vendor_tax_id" in fields else None

            # Look for employee name or DNI patterns in text
            if not emp_nif:
                dni_match = re.search(r"\b([0-9]{8}[A-Z]|[XYZ][0-9]{7}[A-Z])\b", page_text)
                emp_nif = dni_match.group(1) if dni_match else f"EMP_{page_idx + 1:03d}"

            name_match = re.search(r"(?:Trabajador|Empleado|Nombre)[:\s]+([A-ZÁÉÍÓÚÑ\s,]{5,40})", page_text, re.IGNORECASE)
            emp_name = name_match.group(1).strip() if name_match else f"Empleado {page_idx + 1}"

            # Create individual single-page PDF
            single_doc = fitz.open()
            single_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)

            clean_nif = re.sub(r"[^\w]", "", str(emp_nif))
            out_filename = f"nomina_{clean_nif}_pag{page_idx + 1}.pdf"
            out_path = out_dir / out_filename
            single_doc.save(str(out_path))
            single_doc.close()

            splits.append(
                SplitEmployeeRecord(
                    page_number=page_idx + 1,
                    employee_name=emp_name,
                    employee_nif=emp_nif,
                    net_salary=fields.get("total_amount", {}).get("value") if "total_amount" in fields else None,
                    output_filename=out_filename,
                )
            )

        doc.close()

        return PayrollSplitResult(
            total_pages=total_pages,
            employees_detected=len(splits),
            splits=splits,
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
