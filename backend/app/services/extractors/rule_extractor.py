"""Rule-based extractor using regular expressions and fuzzy dictionary matching."""

import re
import time
from typing import Any, Dict, List, Optional
from rapidfuzz import process, fuzz

from app.domain.schemas import (
    ClassificationResult,
    DocumentType,
    ExtractedField,
    ExtractionResult,
)


class RuleExtractor:
    """Extracts key business fields (IDs, dates, amounts, emails) using compiled patterns & fuzzy matching."""

    PATTERNS = {
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        ),
        "tax_id": re.compile(
            r"\b(?:[A-HJ-NP-SUVW]\d{7}[0-9A-J]|\d{8}[A-Z]|[XYZ]\d{7}[A-Z]|[A-Z]{3}\d{6}[A-Z0-9]{3})\b",
            re.IGNORECASE,
        ),
        "invoice_number": re.compile(
            r"(?:\b(?:factura|invoice|n[úu]mero|num|nº|ref)\b|\b(?:fac\.|inv\.))\s*[:#.-]?\s*([A-Za-z0-9-_/]{3,25})\b",
            re.IGNORECASE,
        ),
        "date": re.compile(
            r"\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b"
        ),
        "total_amount": re.compile(
            r"\b(?:total|importe\s*total|total\s*amount|total\s*a\s*pagar|neto)\s*[:=]?\s*([$€£¥]?\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*[$€£¥]?)\b",
            re.IGNORECASE,
        ),
        "iban": re.compile(
            r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]){0,16}\b"
        ),
        "phone": re.compile(
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"
        ),
    }

    CANONICAL_FIELD_ALIASES: Dict[str, List[str]] = {
        "invoice_number": ["factura", "n_factura", "num_factura", "invoice_no", "invoice_number", "numero_factura", "document_no"],
        "issue_date": ["fecha", "fecha_emision", "date", "invoice_date", "issue_date", "f_factura", "fecha_operacion"],
        "due_date": ["fecha_vencimiento", "vencimiento", "due_date", "expiration_date", "f_vencimiento"],
        "tax_id": ["cif", "nif", "vat", "rfc", "cuit", "tax_id", "dni", "identificacion_fiscal"],
        "customer_name": ["cliente", "customer", "client", "razon_social", "comprador", "destinatario", "bill_to"],
        "vendor_name": ["proveedor", "vendor", "emisor", "seller", "empresa", "nombre_comercial"],
        "subtotal": ["base_imponible", "subtotal", "base", "net_amount", "sub_total"],
        "tax_amount": ["iva", "tax", "impuestos", "igic", "vat_amount", "total_iva"],
        "total_amount": ["total", "total_factura", "importe_total", "total_amount", "amount_due", "gran_total", "total_a_pagar"],
        "currency": ["moneda", "currency", "divisa", "curr"],
    }

    def extract_from_text(self, text: str) -> Dict[str, ExtractedField]:
        """Extracts recognizable scalar fields from arbitrary raw text."""
        fields: Dict[str, ExtractedField] = {}

        for key, pattern in self.PATTERNS.items():
            match = pattern.search(text)
            if match:
                raw_val = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                cleaned_val = self._clean_value(key, raw_val)
                fields[key] = ExtractedField(
                    key=key,
                    value=cleaned_val,
                    raw_value=str(raw_val).strip(),
                    confidence=0.85,
                    extractor_type="rule_regex",
                    source_location="text_body",
                )

        return fields

    def match_canonical_field(self, raw_header: str, score_cutoff: float = 75.0) -> Optional[str]:
        """Uses rapidfuzz to map an unstandardized column header to a canonical field key."""
        clean_header = re.sub(r"[_\s-]+", " ", raw_header.lower().strip())

        best_match_key = None
        highest_score = 0.0

        for canonical_key, aliases in self.CANONICAL_FIELD_ALIASES.items():
            result = process.extractOne(
                clean_header,
                aliases,
                scorer=fuzz.WRatio,
                score_cutoff=score_cutoff,
            )
            if result and result[1] > highest_score:
                highest_score = result[1]
                best_match_key = canonical_key

        return best_match_key

    def _clean_value(self, key: str, value: str) -> Any:
        """Normalizes extracted text based on field type."""
        val = value.strip()
        if key in ("total_amount", "subtotal", "tax_amount"):
            # Remove currency symbols and standardize decimals
            sanitized = re.sub(r"[^\d,.-]", "", val)
            if "," in sanitized and "." in sanitized:
                if sanitized.rfind(",") > sanitized.rfind("."):
                    sanitized = sanitized.replace(".", "").replace(",", ".")
                else:
                    sanitized = sanitized.replace(",", "")
            elif "," in sanitized and "." not in sanitized:
                sanitized = sanitized.replace(",", ".")
            try:
                return float(sanitized)
            except ValueError:
                return val
        return val
