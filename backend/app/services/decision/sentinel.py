"""FlowMind Sentinel - Anti-fraud, anomaly detection and continuous continuous auditing engine."""

import hashlib
import math
import re
from typing import Any, Dict, List, Optional
from app.domain.decision_models import (
    SentinelAlert,
    SentinelAlertType,
    SentinelAuditResult,
    SentinelRiskLevel,
)


class FlowMindSentinel:
    """Continuous audit & risk detection engine for invoice fraud, duplicates, and statistical anomalies."""

    def __init__(self, approval_threshold: float = 10000.0):
        self.approval_threshold = approval_threshold

    def clean_iban(self, iban: Optional[str]) -> str:
        if not iban:
            return ""
        return re.sub(r"[\s\-\.]", "", iban).upper().strip()

    def clean_tax_id(self, tax_id: Optional[str]) -> str:
        if not tax_id:
            return ""
        return re.sub(r"[\s\-\.]", "", tax_id).upper().strip()

    def generate_fingerprint(
        self,
        vendor_tax_id: Optional[str],
        invoice_number: Optional[str],
        invoice_date: Optional[str],
        total_amount: Optional[float],
    ) -> str:
        """Generates a canonical hash fingerprint for exact invoice deduplication."""
        t_id = self.clean_tax_id(vendor_tax_id)
        inv_num = re.sub(r"[^\w]", "", (invoice_number or "")).lower()
        inv_date = (invoice_date or "").strip()
        amt_str = f"{total_amount:.2f}" if total_amount is not None else "0.00"

        payload = f"{t_id}|{inv_num}|{inv_date}|{amt_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def check_bank_account_change(
        self,
        vendor_tax_id: str,
        current_iban: str,
        known_vendor_ibans: List[str],
    ) -> Optional[SentinelAlert]:
        """Detects if an invoice specifies a new/unregistered bank account for an established supplier."""
        clean_curr = self.clean_iban(current_iban)
        if not clean_curr:
            return None

        clean_known = [self.clean_iban(ib) for ib in known_vendor_ibans if ib]
        # If vendor has known IBANs and current_iban is NOT among them
        if clean_known and clean_curr not in clean_known:
            return SentinelAlert(
                alert_type=SentinelAlertType.BANK_ACCOUNT_CHANGE,
                risk_level=SentinelRiskLevel.CRITICAL,
                title="Cambio no verificado de Cuenta Bancaria (Alerta de Fraude)",
                description=(
                    f"El proveedor '{vendor_tax_id}' presenta el IBAN '{clean_curr}', "
                    f"el cual no coincide con sus cuentas bancarias históricas ({', '.join(clean_known)})."
                ),
                evidence={
                    "vendor_tax_id": vendor_tax_id,
                    "new_iban": clean_curr,
                    "historical_ibans": clean_known,
                },
                recommended_action=(
                    "Bloquear el pago de forma inmediata y contactar telefónicamente con el proveedor por un canal verificado."
                ),
            )
        return None

    def check_duplicate(
        self,
        document_id: str,
        vendor_tax_id: Optional[str],
        invoice_number: Optional[str],
        invoice_date: Optional[str],
        total_amount: Optional[float],
        historical_records: List[Dict[str, Any]],
    ) -> Optional[SentinelAlert]:
        """Checks if an identical or near-duplicate invoice has already been registered."""
        if not vendor_tax_id or not invoice_number or total_amount is None:
            return None

        current_fp = self.generate_fingerprint(vendor_tax_id, invoice_number, invoice_date, total_amount)
        clean_curr_num = re.sub(r"[^\w]", "", invoice_number).lower()
        clean_curr_tax = self.clean_tax_id(vendor_tax_id)

        for hist in historical_records:
            if hist.get("document_id") == document_id:
                continue

            hist_fp = hist.get("fingerprint") or self.generate_fingerprint(
                hist.get("vendor_tax_id"),
                hist.get("invoice_number"),
                hist.get("invoice_date"),
                hist.get("total_amount"),
            )

            # Exact fingerprint match
            if current_fp == hist_fp:
                return SentinelAlert(
                    alert_type=SentinelAlertType.MULTIDIMENSIONAL_DUPLICATE,
                    risk_level=SentinelRiskLevel.HIGH,
                    title="Factura Duplicada Detectada (Coincidencia Exacta)",
                    description=(
                        f"Ya existe una factura registrada con el mismo emisor ({vendor_tax_id}), "
                        f"número ({invoice_number}) e importe ({total_amount:.2f}€) [Doc ID: {hist.get('document_id')}]."
                    ),
                    evidence={
                        "existing_document_id": hist.get("document_id"),
                        "fingerprint": current_fp,
                    },
                    recommended_action="Verificar si se trata de un reenvío accidental o una doble contabilización.",
                )

            # Fuzzy duplicate: Same vendor + Same amount + similar invoice number
            hist_tax = self.clean_tax_id(hist.get("vendor_tax_id"))
            hist_num = re.sub(r"[^\w]", "", hist.get("invoice_number") or "").lower()
            hist_amt = hist.get("total_amount")

            if (
                clean_curr_tax == hist_tax
                and hist_amt is not None
                and abs(hist_amt - total_amount) < 0.01
                and (clean_curr_num == hist_num or clean_curr_num in hist_num or hist_num in clean_curr_num)
            ):
                return SentinelAlert(
                    alert_type=SentinelAlertType.MULTIDIMENSIONAL_DUPLICATE,
                    risk_level=SentinelRiskLevel.MEDIUM,
                    title="Posible Factura Duplicada (Coincidencia Difusa)",
                    description=(
                        f"Coincidencia de proveedor ({vendor_tax_id}) e importe exacto ({total_amount:.2f}€) "
                        f"con la factura #{hist.get('invoice_number')} previamente registrada."
                    ),
                    evidence={
                        "existing_document_id": hist.get("document_id"),
                        "existing_invoice_number": hist.get("invoice_number"),
                    },
                    recommended_action="Revisar manualmente el documento para descartar duplicidad.",
                )

        return None

    def check_threshold_avoidance(
        self,
        current_amount: float,
        recent_amounts: List[float],
        margin_pct: float = 0.05,
        min_occurrences: int = 3,
    ) -> Optional[SentinelAlert]:
        """Detects patterns of transactions suspiciously placed just below the executive approval threshold."""
        lower_bound = self.approval_threshold * (1.0 - margin_pct)
        upper_bound = self.approval_threshold

        all_amounts = recent_amounts + [current_amount]
        clustered = [a for a in all_amounts if lower_bound <= a < upper_bound]

        if len(clustered) >= min_occurrences and (lower_bound <= current_amount < upper_bound):
            return SentinelAlert(
                alert_type=SentinelAlertType.THRESHOLD_AVOIDANCE,
                risk_level=SentinelRiskLevel.MEDIUM,
                title="Patrón de Evasión de Umbral de Aprobación Detectado",
                description=(
                    f"Se han detectado {len(clustered)} operaciones consecutivas situadas justo por debajo "
                    f"del límite de aprobación ejecutiva de {self.approval_threshold:.2f}€ (rango {lower_bound:.2f}€ - {upper_bound:.2f}€)."
                ),
                evidence={
                    "threshold": self.approval_threshold,
                    "clustered_amounts": clustered,
                },
                recommended_action="Requerir aprobación a cuatro ojos (Four-Eyes Review) por política de control interno.",
            )
        return None

    def check_benford_law(self, amounts: List[float]) -> Optional[SentinelAlert]:
        """Performs Benford's Law First-Digit Analysis on a collection of amounts."""
        valid_digits = []
        for a in amounts:
            if a > 0:
                s = str(a).lstrip("0").replace(".", "").replace(",", "")
                if s and s[0].isdigit() and s[0] != "0":
                    valid_digits.append(int(s[0]))

        if len(valid_digits) < 50:
            return None  # Sample size too small for statistical significance

        n = len(valid_digits)
        observed_counts = {d: valid_digits.count(d) for d in range(1, 10)}
        expected_counts = {d: n * math.log10(1 + 1 / d) for d in range(1, 10)}

        # Compute Chi-Square statistic
        chi_square = sum(
            ((observed_counts[d] - expected_counts[d]) ** 2) / expected_counts[d]
            for d in range(1, 10)
        )

        # Critical value for 8 degrees of freedom at alpha=0.01 is 20.09
        if chi_square > 20.09:
            return SentinelAlert(
                alert_type=SentinelAlertType.BENFORD_ANOMALY,
                risk_level=SentinelRiskLevel.MEDIUM,
                title="Desviación Estadística en Ley de Benford",
                description=(
                    f"La distribución de los primeros dígitos en el lote ({n} transacciones, Chi² = {chi_square:.2f}) "
                    f"muestra una anomalía estadística respecto a los patrones naturales de facturación."
                ),
                evidence={
                    "chi_square": round(chi_square, 2),
                    "sample_size": n,
                    "observed": observed_counts,
                },
                recommended_action="Realizar muestreo de auditoría interna sobre las transacciones del lote.",
            )
        return None

    def audit_document(
        self,
        document_id: str,
        vendor_tax_id: Optional[str] = None,
        invoice_number: Optional[str] = None,
        invoice_date: Optional[str] = None,
        total_amount: Optional[float] = None,
        iban: Optional[str] = None,
        known_vendor_ibans: Optional[List[str]] = None,
        historical_records: Optional[List[Dict[str, Any]]] = None,
        recent_amounts: Optional[List[float]] = None,
    ) -> SentinelAuditResult:
        """Runs the complete suite of Sentinel security and fraud audits for a document."""
        alerts: List[SentinelAlert] = []

        # 1. Check Bank Account Change
        if vendor_tax_id and iban and known_vendor_ibans:
            alert = self.check_bank_account_change(vendor_tax_id, iban, known_vendor_ibans)
            if alert:
                alerts.append(alert)

        # 2. Check Duplicates
        if historical_records:
            alert = self.check_duplicate(
                document_id=document_id,
                vendor_tax_id=vendor_tax_id,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                total_amount=total_amount,
                historical_records=historical_records,
            )
            if alert:
                alerts.append(alert)

        # 3. Check Threshold Avoidance
        if total_amount is not None and recent_amounts:
            alert = self.check_threshold_avoidance(total_amount, recent_amounts)
            if alert:
                alerts.append(alert)

        # Determine highest risk level and risk score
        risk_map = {
            SentinelRiskLevel.LOW: 0.1,
            SentinelRiskLevel.MEDIUM: 0.4,
            SentinelRiskLevel.HIGH: 0.75,
            SentinelRiskLevel.CRITICAL: 1.0,
        }

        highest_risk = SentinelRiskLevel.LOW
        if any(a.risk_level == SentinelRiskLevel.CRITICAL for a in alerts):
            highest_risk = SentinelRiskLevel.CRITICAL
        elif any(a.risk_level == SentinelRiskLevel.HIGH for a in alerts):
            highest_risk = SentinelRiskLevel.HIGH
        elif any(a.risk_level == SentinelRiskLevel.MEDIUM for a in alerts):
            highest_risk = SentinelRiskLevel.MEDIUM

        risk_score = risk_map[highest_risk] if alerts else 0.0

        return SentinelAuditResult(
            total_alerts=len(alerts),
            highest_risk=highest_risk,
            alerts=alerts,
            risk_score=risk_score,
        )
