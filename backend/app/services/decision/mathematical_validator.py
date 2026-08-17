"""Deterministic mathematical validator for business documents (invoices, purchase orders, payroll)."""

from typing import Dict, List, Optional
from app.domain.decision_models import (
    DiscrepancySeverity,
    LineItemInput,
    MathematicalValidationResult,
    ValidationFinding,
)


class MathematicalDocumentValidator:
    """Recalculates line items, tax group subtotals, withholdings, and validates invoice totals."""

    def __init__(self, rounding_tolerance: float = 0.02):
        self.rounding_tolerance = rounding_tolerance

    def validate_invoice(
        self,
        lines: List[LineItemInput],
        document_subtotal: Optional[float] = None,
        document_tax: Optional[float] = None,
        document_total: Optional[float] = None,
        withholding_pct: float = 0.0,
        shipping_cost: float = 0.0,
    ) -> MathematicalValidationResult:
        findings: List[ValidationFinding] = []
        calculated_subtotal = 0.0
        tax_groups: Dict[float, float] = {}

        # 1. Validate and sum each line item
        for idx, line in enumerate(lines, 1):
            discount_factor = 1.0 - (line.discount_pct / 100.0)
            expected_line_total = round(line.quantity * line.unit_price * discount_factor, 2)
            calculated_subtotal += expected_line_total

            # Accumulate base per tax rate group
            rate = round(line.tax_rate_pct, 2)
            tax_groups[rate] = tax_groups.get(rate, 0.0) + expected_line_total

            # Verify line total if provided
            if line.line_total is not None:
                line_dev = abs(line.line_total - expected_line_total)
                if line_dev > self.rounding_tolerance:
                    findings.append(
                        ValidationFinding(
                            category="line_item_total",
                            severity=DiscrepancySeverity.CRITICAL if line_dev > 1.0 else DiscrepancySeverity.WARNING,
                            description=(
                                f"Línea #{idx} ({line.description or 'Item'}): Total declarado {line.line_total:.2f}€ "
                                f"difiere del cálculo ({line.quantity} × {line.unit_price:.2f}€ - {line.discount_pct}% = {expected_line_total:.2f}€)."
                            ),
                            expected_value=expected_line_total,
                            actual_value=line.line_total,
                            deviation=round(line_dev, 2),
                        )
                    )

        calculated_subtotal = round(calculated_subtotal, 2)

        # 2. Compute taxes per tax rate group
        calculated_tax = 0.0
        for rate, base in tax_groups.items():
            group_tax = round(base * (rate / 100.0), 2)
            calculated_tax += group_tax

        calculated_tax = round(calculated_tax, 2)

        # 3. Calculate withholding and final total
        withholding_amount = round(calculated_subtotal * (withholding_pct / 100.0), 2)
        calculated_total = round(calculated_subtotal + calculated_tax - withholding_amount + shipping_cost, 2)

        # 4. Compare with declared document subtotal
        if document_subtotal is not None:
            subtotal_dev = abs(document_subtotal - calculated_subtotal)
            if subtotal_dev > self.rounding_tolerance:
                findings.append(
                    ValidationFinding(
                        category="subtotal_check",
                        severity=DiscrepancySeverity.CRITICAL if subtotal_dev > 1.0 else DiscrepancySeverity.WARNING,
                        description=(
                            f"Base imponible declarada ({document_subtotal:.2f}€) no coincide con la suma de líneas calculada ({calculated_subtotal:.2f}€)."
                        ),
                        expected_value=calculated_subtotal,
                        actual_value=document_subtotal,
                        deviation=round(subtotal_dev, 2),
                    )
                )

        # 5. Compare with declared document tax
        if document_tax is not None:
            tax_dev = abs(document_tax - calculated_tax)
            if tax_dev > self.rounding_tolerance:
                findings.append(
                    ValidationFinding(
                        category="tax_check",
                        severity=DiscrepancySeverity.CRITICAL if tax_dev > 1.0 else DiscrepancySeverity.WARNING,
                        description=(
                            f"Cuota de IVA declarada ({document_tax:.2f}€) difiere de la cuota calculada ({calculated_tax:.2f}€)."
                        ),
                        expected_value=calculated_tax,
                        actual_value=document_tax,
                        deviation=round(tax_dev, 2),
                    )
                )

        # 6. Compare with declared document total
        total_deviation = 0.0
        if document_total is not None:
            total_deviation = round(abs(document_total - calculated_total), 2)
            if total_deviation > self.rounding_tolerance:
                findings.append(
                    ValidationFinding(
                        category="total_check",
                        severity=DiscrepancySeverity.CRITICAL if total_deviation > 1.0 else DiscrepancySeverity.WARNING,
                        description=(
                            f"Total general declarado ({document_total:.2f}€) difiere del total aritmético recalculado ({calculated_total:.2f}€). Desviación: {total_deviation:.2f}€."
                        ),
                        expected_value=calculated_total,
                        actual_value=document_total,
                        deviation=total_deviation,
                    )
                )

        has_critical = any(f.severity == DiscrepancySeverity.CRITICAL for f in findings)
        is_valid = not has_critical and total_deviation <= self.rounding_tolerance

        return MathematicalValidationResult(
            is_valid=is_valid,
            calculated_subtotal=calculated_subtotal,
            calculated_tax=calculated_tax,
            calculated_total=calculated_total,
            document_total=document_total,
            deviation=total_deviation,
            findings=findings,
        )
