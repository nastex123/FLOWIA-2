"""Veri*factu & TicketBAI Hash-Chaining & Fiscal Integrity Engine (RD 1007/2023)."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Optional

from app.domain.compliance_models import (
    VerifactuChainingRequest,
    VerifactuChainingResult,
)


class VerifactuEngine:
    """Computes immutable SHA-256 chained hashes and QR verification payloads for Spanish Veri*factu systems."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"
    AEAT_VERIFACTU_URL = "https://sede.agenciatributaria.gob.es/verifactu"

    def compute_chained_hash(self, request: VerifactuChainingRequest) -> VerifactuChainingResult:
        prev_hash = request.previous_invoice_hash or self.GENESIS_HASH
        timestamp = request.timestamp_iso or datetime.now(timezone.utc).isoformat()

        clean_nif = re.sub(r"[\s\-\.]", "", request.issuer_nif).upper()
        clean_num = request.invoice_series_number.strip()
        date_str = request.issue_date.strip()

        # Canonical hashing payload string
        payload = (
            f"{prev_hash}|"
            f"{clean_nif}|"
            f"{clean_num}|"
            f"{date_str}|"
            f"{request.invoice_type}|"
            f"{request.total_tax_quota:.2f}|"
            f"{request.total_amount:.2f}|"
            f"{timestamp}"
        )

        current_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()

        # Build official AEAT Veri*factu verification QR URL
        qr_url = (
            f"{self.AEAT_VERIFACTU_URL}?"
            f"nif={clean_nif}&"
            f"num={clean_num}&"
            f"fec={date_str}&"
            f"imp={request.total_amount:.2f}&"
            f"hc={current_hash[:8]}"
        )

        summary = f"Chained to previous: {prev_hash[:12]}... | Fingerprint: {current_hash[:16]}..."

        return VerifactuChainingResult(
            current_hash=current_hash,
            previous_hash=prev_hash,
            qr_payload_url=qr_url,
            signature_summary=summary,
        )
