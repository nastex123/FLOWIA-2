"""Local PII and GDPR Redactor for sensitive document information."""

import re
from typing import List
from app.domain.compliance_models import (
    PIIRedactionRequest,
    PIIRedactionResult,
    RedactedSpan,
)


class PIIRedactor:
    """Anonymizes and redacts personal identifiable information (PII) from document texts."""

    PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "IBAN": r"\b[A-Z]{2}\d{2}[\s\-]?(?:\d{4}[\s\-]?){4,7}\d{1,4}\b",
        "NIF_DNI": r"\b(?:\d{8}[A-HJ-NP-TV-Z]|[XYZ]\d{7}[A-HJ-NP-TV-Z]|[A-HJ-NP-SUVW]\d{7}[0-9A-J])\b",
        "PHONE": r"(?:\+34|0034)?[\s\-]?[6789]\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b",
        "CARD": r"\b(?:\d{4}[\s\-]?){3}\d{4}\b",
    }

    def redact(self, request: PIIRedactionRequest) -> PIIRedactionResult:
        text = request.text
        redactions: List[RedactedSpan] = []

        # 1. Redact IBAN
        if request.mask_iban:
            for match in re.finditer(self.PATTERNS["IBAN"], text):
                redactions.append(
                    RedactedSpan(
                        pii_type="IBAN",
                        original_snippet=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
            text = re.sub(self.PATTERNS["IBAN"], "[REDACTED_IBAN]", text)

        # 2. Redact Email
        if request.mask_email:
            for match in re.finditer(self.PATTERNS["EMAIL"], text):
                redactions.append(
                    RedactedSpan(
                        pii_type="EMAIL",
                        original_snippet=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
            text = re.sub(self.PATTERNS["EMAIL"], "[REDACTED_EMAIL]", text)

        # 3. Redact NIF/DNI/CIF
        if request.mask_nif:
            for match in re.finditer(self.PATTERNS["NIF_DNI"], text):
                redactions.append(
                    RedactedSpan(
                        pii_type="NIF_DNI",
                        original_snippet=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
            text = re.sub(self.PATTERNS["NIF_DNI"], "[REDACTED_NIF]", text)

        # 4. Redact Phone
        if request.mask_phone:
            for match in re.finditer(self.PATTERNS["PHONE"], text):
                redactions.append(
                    RedactedSpan(
                        pii_type="PHONE",
                        original_snippet=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
            text = re.sub(self.PATTERNS["PHONE"], "[REDACTED_PHONE]", text)

        return PIIRedactionResult(
            sanitized_text=text,
            total_redactions=len(redactions),
            redactions=redactions,
        )
