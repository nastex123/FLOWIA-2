"""Rule-based heuristic classifier using keyword density and document patterns."""

import re
from typing import Any, Dict, List, Optional

from app.domain.schemas import ClassificationResult, DocumentType
from app.services.classifiers.base import BaseClassifier


class RuleClassifier(BaseClassifier):
    """Categorizes text content based on high-precision keyword rules and heuristics."""

    KEYWORDS_MAP: Dict[DocumentType, List[str]] = {
        DocumentType.INVOICE: [
            "factura", "invoice", "cif", "nif", "iva", "base imponible",
            "importe total", "total factura", "tax id", "amount due",
            "vencimiento", "albarán", "bill to", "tax invoice",
        ],
        DocumentType.PURCHASE_ORDER: [
            "pedido", "orden de compra", "purchase order", "po number",
            "nº pedido", "shipping address", "proveedor", "order date",
        ],
        DocumentType.PAYROLL: [
            "nómina", "nomina", "recibo de salarios", "devengos", "deducciones",
            "líquido a percibir", "irpf", "seguridad social", "base cotización",
            "salario base", "antigüedad", "payroll", "payslip",
        ],
        DocumentType.INVENTORY: [
            "inventario", "stock", "sku", "existencias", "unidades",
            "almacén", "reorden", "catalogo", "inventory", "warehouse",
        ],
        DocumentType.CONTRACT: [
            "contrato", "cláusula", "acuerdo", "estipulaciones",
            "partes comparecientes", "arrendamiento", "confidencialidad",
            "terms and conditions", "hereby agree",
        ],
        DocumentType.FINANCIAL_REPORT: [
            "balance de situación", "cuenta de pérdidas y ganancias",
            "ejercicio contable", "ebitda", "flujo de caja", "cash flow",
            "auditoría", "activo corriente", "pasivo corriente",
        ],
    }

    def classify(
        self,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        if not text_content or not text_content.strip():
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                classifier_type="rule_based",
                matched_features=[],
            )

        lower_text = text_content.lower()
        best_type = DocumentType.UNKNOWN
        max_matches = 0
        best_features: List[str] = []

        for doc_type, keywords in self.KEYWORDS_MAP.items():
            matched = [kw for kw in keywords if kw in lower_text]
            count = len(matched)
            if count > max_matches:
                max_matches = count
                best_type = doc_type
                best_features = matched

        if max_matches == 0:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                classifier_type="rule_based",
                matched_features=[],
            )

        # Calculate a calibrated confidence score based on matches
        confidence = min(0.5 + (max_matches * 0.1), 0.98)

        return ClassificationResult(
            document_type=best_type,
            confidence=round(confidence, 2),
            classifier_type="rule_based",
            matched_features=best_features,
        )
