"""Deterministic Invoice Structurizer to convert ExtractionResult into StructuredInvoice."""

from datetime import date, datetime
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
import re
from rapidfuzz import fuzz

from app.domain.invoice_models import (
    InvoiceLineItem,
    StructuredInvoice,
    TaxBreakdownItem,
)
from app.services.mapping.schema_normalizer import SchemaNormalizer


def _normalize_text(text: str) -> str:
    """Removes accents and punctuation for normalized string comparison."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(text))
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    cleaned = re.sub(r"[_\-\.\(\)\[\]/,:;]", " ", ascii_text.lower()).strip()
    return re.sub(r"\s+", " ", cleaned)


class InvoiceStructurizer:
    """Transforms raw document extraction outputs (fields and tables) into a structured invoice model."""

    HEADER_FIELD_MAPPINGS = {
        "invoice_number": ["invoice_number", "factura_num", "num_factura", "numero_factura", "factura_no", "invoice_no", "n_factura", "factura", "num"],
        "vendor_name": ["vendor_name", "emisor", "proveedor", "empresa", "razon_social", "nombre_emisor", "sociedad"],
        "vendor_tax_id": ["vendor_tax_id", "tax_id", "cif_nif", "cif", "nif", "cif_emisor", "nif_emisor", "vat_number", "cif proveedor", "nif proveedor"],
        "customer_name": ["customer_name", "cliente", "receptor", "nombre_cliente", "destinatario", "cliente nombre"],
        "customer_tax_id": ["customer_tax_id", "cif_receptor", "nif_cliente", "cliente_cif", "nif_receptor", "cif cliente"],
        "issue_date": ["issue_date", "invoice_date", "fecha_emision", "fecha_factura", "fecha", "emision"],
        "due_date": ["due_date", "fecha_vencimiento", "vencimiento", "fecha limite"],
        "currency": ["currency", "divisa", "moneda"],
        "subtotal": ["subtotal", "base_imponible", "base_total", "net_amount", "base", "sub total"],
        "tax_total": ["tax_amount", "tax_total", "total_iva", "cuota_iva", "iva", "impuestos", "cuota total"],
        "total_amount": ["total_amount", "total_factura", "total", "importe_total", "importe", "total a pagar"],
        "withholding_amount": ["withholding_amount", "retencion", "irpf", "retencion_irpf", "retencion irpf"],
        "shipping_amount": ["shipping_amount", "gastos_envio", "portes", "envio", "transporte"],
    }

    LINE_ITEM_COLUMN_CANDIDATES = {
        "description": ["description", "descripcion", "concepto", "articulo", "item", "detalle", "producto", "servicio", "denominacion"],
        "quantity": ["quantity", "cantidad", "cant", "unidades", "uds", "qty", "unid", "horas"],
        "unit_price": ["unit_price", "precio_unitario", "precio_ud", "precio", "p_unit", "pvu", "rate", "price", "precio/ud", "p unit"],
        "discount_pct": ["discount_pct", "descuento", "dto", "dto_%", "%_dto", "desc", "% dto"],
        "tax_rate_pct": ["tax_rate_pct", "tax_rate", "tipo_iva", "iva_%", "%_iva", "iva", "%_tipo", "% iva", "tipo iva", "iva %"],
        "line_total": ["line_total", "importe", "total", "total_linea", "subtotal_linea", "base", "amount", "total_neto", "total linea", "importe linea"],
    }

    def __init__(self):
        self.normalizer = SchemaNormalizer()

    def structurize(
        self,
        extraction_result: Any,
        document_id: str,
    ) -> StructuredInvoice:
        """Converts extraction fields and tables into a canonical StructuredInvoice."""
        # 1. Unpack fields and tables from extraction_result
        fields_dict: Dict[str, Any] = {}
        tables_list: List[Any] = []

        if hasattr(extraction_result, "fields"):
            for k, v in extraction_result.fields.items():
                fields_dict[k] = getattr(v, "value", v)
        elif isinstance(extraction_result, dict):
            raw_fields = extraction_result.get("fields", extraction_result)
            if isinstance(raw_fields, dict):
                for k, v in raw_fields.items():
                    if isinstance(v, dict) and "value" in v:
                        fields_dict[k] = v["value"]
                    else:
                        fields_dict[k] = v

        if hasattr(extraction_result, "tables"):
            tables_list = extraction_result.tables
        elif isinstance(extraction_result, dict):
            tables_list = extraction_result.get("tables", [])

        # 2. Extract header fields
        extracted_headers = self._extract_headers(fields_dict)

        # 3. Extract line items from the best candidate table
        line_items = self._extract_line_items(tables_list)

        # 4. Compute Tax Breakdown
        tax_breakdown = self._build_tax_breakdown(
            line_items=line_items,
            declared_subtotal=extracted_headers.get("subtotal"),
            declared_tax=extracted_headers.get("tax_total"),
        )

        # 5. Determine totals and derive if missing
        subtotal = extracted_headers.get("subtotal")
        tax_total = extracted_headers.get("tax_total")
        total_amount = extracted_headers.get("total_amount")
        withholding = extracted_headers.get("withholding_amount") or 0.0
        shipping = extracted_headers.get("shipping_amount") or 0.0

        if subtotal is None and line_items:
            subtotal = round(sum(
                (item.line_total if item.line_total is not None else ((item.quantity or 1.0) * (item.unit_price or 0.0) * (1.0 - (item.discount_pct or 0.0) / 100.0)))
                for item in line_items
            ), 2)

        if tax_total is None and tax_breakdown:
            tax_total = round(sum(tb.tax_quota for tb in tax_breakdown), 2)

        if total_amount is None:
            if subtotal is not None:
                total_amount = round((subtotal or 0.0) + (tax_total or 0.0) - withholding + shipping, 2)

        return StructuredInvoice(
            document_id=document_id,
            invoice_number=extracted_headers.get("invoice_number"),
            vendor_name=extracted_headers.get("vendor_name"),
            vendor_tax_id=extracted_headers.get("vendor_tax_id"),
            customer_name=extracted_headers.get("customer_name"),
            customer_tax_id=extracted_headers.get("customer_tax_id"),
            issue_date=extracted_headers.get("issue_date"),
            due_date=extracted_headers.get("due_date"),
            currency=extracted_headers.get("currency") or "EUR",
            items=line_items,
            tax_breakdown=tax_breakdown,
            subtotal=subtotal,
            tax_total=tax_total,
            total_amount=total_amount,
            withholding_amount=extracted_headers.get("withholding_amount"),
            shipping_amount=extracted_headers.get("shipping_amount"),
        )

    def _clean_number(self, val: Any) -> Optional[float]:
        """Cleans and normalizes numeric values from raw strings with symbols."""
        if val is None or val == "":
            return None
        val_str = str(val).replace("%", "").replace("€", "").replace("$", "").replace("£", "").strip()
        norm_val, _ = self.normalizer.normalize_value(val_str, "number")
        return float(norm_val) if norm_val is not None else None

    def _extract_headers(self, fields_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Maps extracted fields dictionary to canonical header fields."""
        results: Dict[str, Any] = {}

        # Normalize key names for quick matching
        cleaned_source: Dict[str, Any] = {}
        for k, v in fields_dict.items():
            if v is not None and v != "":
                clean_k = _normalize_text(k).replace(" ", "")
                cleaned_source[clean_k] = v

        for canonical_name, aliases in self.HEADER_FIELD_MAPPINGS.items():
            best_val = None

            # First: exact match by alias
            for alias in aliases:
                clean_alias = _normalize_text(alias).replace(" ", "")
                if clean_alias in cleaned_source:
                    best_val = cleaned_source[clean_alias]
                    break

            # Second: fuzzy match against source keys if not found
            if best_val is None:
                for k, v in fields_dict.items():
                    if v is None or v == "":
                        continue
                    clean_k = _normalize_text(k)
                    for alias in aliases:
                        clean_alias = _normalize_text(alias)
                        if fuzz.token_sort_ratio(clean_k, clean_alias) >= 85:
                            best_val = v
                            break
                    if best_val is not None:
                        break

            if best_val is not None:
                results[canonical_name] = self._cast_header_value(canonical_name, best_val)

        return results

    def _cast_header_value(self, canonical_name: str, raw_val: Any) -> Any:
        """Casts raw header value to expected data type."""
        if canonical_name in ("subtotal", "tax_total", "total_amount", "withholding_amount", "shipping_amount"):
            return self._clean_number(raw_val)

        if canonical_name in ("issue_date", "due_date"):
            val, _ = self.normalizer.normalize_value(raw_val, "date")
            if isinstance(val, date):
                return val
            if isinstance(val, datetime):
                return val.date()
            if isinstance(val, str):
                try:
                    return datetime.fromisoformat(val).date()
                except Exception:
                    return None
            return None

        if canonical_name == "currency":
            val_str = str(raw_val).strip().upper()
            if "EUR" in val_str or "€" in val_str:
                return "EUR"
            if "USD" in val_str or "$" in val_str:
                return "USD"
            if "GBP" in val_str or "£" in val_str:
                return "GBP"
            return val_str[:3] if val_str else "EUR"

        # String fields: clean whitespace
        return str(raw_val).strip()

    def _extract_line_items(self, tables: List[Any]) -> List[InvoiceLineItem]:
        """Finds table corresponding to line items and converts rows into InvoiceLineItem objects."""
        if not tables:
            return []

        best_table = None
        best_mapping: Dict[str, str] = {}
        highest_score = 0.0

        for table in tables:
            headers = []
            rows = []
            if hasattr(table, "headers"):
                headers = table.headers or []
                rows = getattr(table, "rows", [])
            elif isinstance(table, dict):
                headers = table.get("headers", [])
                rows = table.get("rows", [])

            if not headers or not rows:
                continue

            mapping, score = self._match_table_columns(headers)
            if score > highest_score and score >= 0.25:
                highest_score = score
                best_table = (headers, rows)
                best_mapping = mapping

        if not best_table or not best_mapping:
            return []

        headers, rows = best_table
        items: List[InvoiceLineItem] = []

        for row in rows:
            row_dict: Dict[str, Any] = {}
            if isinstance(row, dict):
                row_dict = row
            elif isinstance(row, (list, tuple)):
                for idx, cell in enumerate(row):
                    if idx < len(headers):
                        row_dict[headers[idx]] = cell

            # Build line item
            desc_col = best_mapping.get("description")
            desc_val = str(row_dict.get(desc_col, "")).strip() if desc_col else ""
            if not desc_val and not any(row_dict.values()):
                continue

            qty_col = best_mapping.get("quantity")
            qty = self._clean_number(row_dict.get(qty_col)) if qty_col else 1.0
            if qty is None:
                qty = 1.0

            price_col = best_mapping.get("unit_price")
            price = self._clean_number(row_dict.get(price_col)) if price_col else None

            disc_col = best_mapping.get("discount_pct")
            discount = self._clean_number(row_dict.get(disc_col)) if disc_col else 0.0
            if discount is None:
                discount = 0.0

            tax_col = best_mapping.get("tax_rate_pct")
            tax_rate = self._clean_number(row_dict.get(tax_col)) if tax_col else None

            total_col = best_mapping.get("line_total")
            line_total = self._clean_number(row_dict.get(total_col)) if total_col else None

            # Calculate total if not provided and price is available
            if line_total is None and price is not None:
                line_total = round(qty * price * (1.0 - (discount / 100.0)), 2)

            items.append(
                InvoiceLineItem(
                    description=desc_val or f"Item {len(items) + 1}",
                    quantity=qty,
                    unit_price=price,
                    discount_pct=discount,
                    tax_rate_pct=tax_rate,
                    line_total=line_total,
                )
            )

        return items

    def _match_table_columns(self, headers: List[str]) -> Tuple[Dict[str, str], float]:
        """Matches table headers to canonical line item columns using rapidfuzz and normalized text."""
        mapping: Dict[str, str] = {}
        matched_canonical = set()
        total_score = 0.0

        for col in headers:
            clean_col = _normalize_text(col)
            best_target = None
            best_score = 0.0

            for target_name, candidates in self.LINE_ITEM_COLUMN_CANDIDATES.items():
                if target_name in matched_canonical:
                    continue
                for cand in candidates:
                    clean_cand = _normalize_text(cand)
                    if clean_col == clean_cand:
                        best_score = 1.0
                        best_target = target_name
                        break
                    score = fuzz.token_sort_ratio(clean_col, clean_cand) / 100.0
                    if score > best_score and score >= 0.70:
                        best_score = score
                        best_target = target_name

            if best_target and best_score >= 0.70 and best_target not in matched_canonical:
                mapping[best_target] = col
                matched_canonical.add(best_target)
                total_score += best_score

        # Table must match at least description, line_total, or unit_price to be considered valid
        has_essential = "description" in mapping or "line_total" in mapping or "unit_price" in mapping
        overall_score = (total_score / max(len(mapping), 1)) if (has_essential and len(mapping) >= 1) else 0.0
        return mapping, overall_score

    def _build_tax_breakdown(
        self,
        line_items: List[InvoiceLineItem],
        declared_subtotal: Optional[float],
        declared_tax: Optional[float],
    ) -> List[TaxBreakdownItem]:
        """Constructs tax breakdown items grouped by tax rate."""
        # 1. If line items have explicit tax rates and lines exist
        lines_with_tax = [item for item in line_items if item.tax_rate_pct is not None and item.line_total is not None]
        if lines_with_tax:
            groups: Dict[float, float] = {}
            for item in lines_with_tax:
                rate = round(float(item.tax_rate_pct or 0.0), 2)
                base = item.line_total or 0.0
                groups[rate] = groups.get(rate, 0.0) + base

            breakdown: List[TaxBreakdownItem] = []
            for rate, base in sorted(groups.items()):
                quota = round(base * (rate / 100.0), 2)
                breakdown.append(
                    TaxBreakdownItem(
                        tax_rate_pct=rate,
                        taxable_base=round(base, 2),
                        tax_quota=quota,
                    )
                )
            return breakdown

        # 2. Single breakdown item from declared header values
        if declared_subtotal is not None and declared_tax is not None and declared_subtotal > 0:
            effective_rate = round((declared_tax / declared_subtotal) * 100.0, 2)
            return [
                TaxBreakdownItem(
                    tax_rate_pct=effective_rate,
                    taxable_base=round(declared_subtotal, 2),
                    tax_quota=round(declared_tax, 2),
                )
            ]

        return []
