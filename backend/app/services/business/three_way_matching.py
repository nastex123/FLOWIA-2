"""3-Way Matching Engine: Purchase Order (PO) vs Goods Receipt (GR) vs Invoice."""

from typing import List
from app.domain.business_models import (
    MatchLineFinding,
    MatchLineItemInput,
    MatchStatus,
    ThreeWayMatchResult,
)


class ThreeWayMatchingEngine:
    """Matches line items and totals across PO, Goods Receipt, and Invoice with tolerance bands."""

    def reconcile(
        self,
        po_number: str,
        invoice_number: str,
        lines: List[MatchLineItemInput],
        qty_tolerance_pct: float = 1.0,
        price_tolerance_pct: float = 0.5,
    ) -> ThreeWayMatchResult:
        findings: List[MatchLineFinding] = []
        total_po_amount = 0.0
        total_invoice_amount = 0.0
        total_variance_amount = 0.0
        has_critical_error = False
        has_warning = False

        for idx, line in enumerate(lines, 1):
            po_line_total = round(line.ordered_qty * line.po_unit_price, 2)
            inv_line_total = round(line.invoiced_qty * line.invoice_unit_price, 2)

            total_po_amount += po_line_total
            total_invoice_amount += inv_line_total

            qty_diff = round(line.invoiced_qty - line.received_qty, 2)
            price_diff = round(line.invoice_unit_price - line.po_unit_price, 2)
            line_var = round(inv_line_total - po_line_total, 2)
            total_variance_amount += line_var

            line_status = MatchStatus.APPROVED
            messages = []

            # 1. Check Quantity Discrepancy (Invoiced vs Received)
            if line.received_qty > 0:
                qty_pct = abs(qty_diff / line.received_qty) * 100.0
            else:
                qty_pct = 100.0 if line.invoiced_qty > 0 else 0.0

            if qty_diff > 0:
                if qty_pct > qty_tolerance_pct:
                    line_status = MatchStatus.REJECTED
                    has_critical_error = True
                    messages.append(
                        f"Cantidad facturada ({line.invoiced_qty}) supera la recibida en albarán ({line.received_qty}). Exceso: +{qty_diff} uds."
                    )
                else:
                    line_status = MatchStatus.FLAGGED
                    has_warning = True
                    messages.append(f"Ligero exceso de cantidad dentro de tolerancia ({qty_diff} uds).")

            # 2. Check Price Discrepancy (Invoiced vs PO Unit Price)
            if line.po_unit_price > 0:
                price_pct = abs(price_diff / line.po_unit_price) * 100.0
            else:
                price_pct = 100.0 if line.invoice_unit_price > 0 else 0.0

            if price_diff > 0:
                if price_pct > price_tolerance_pct:
                    line_status = MatchStatus.REJECTED
                    has_critical_error = True
                    messages.append(
                        f"Precio unitario ({line.invoice_unit_price:.2f}€) superior al pactado en pedido ({line.po_unit_price:.2f}€). Sobrecoste: +{price_diff:.2f}€/ud."
                    )
                else:
                    if line_status == MatchStatus.APPROVED:
                        line_status = MatchStatus.FLAGGED
                    has_warning = True
                    messages.append(f"Variación de precio dentro de tolerancia (+{price_diff:.2f}€).")

            if not messages:
                messages.append("Línea conciliada perfectamente (100% Match).")

            findings.append(
                MatchLineFinding(
                    sku=line.sku,
                    description=line.description,
                    qty_discrepancy=qty_diff,
                    price_discrepancy=price_diff,
                    line_variance=line_var,
                    status=line_status,
                    message=" | ".join(messages),
                )
            )

        total_po_amount = round(total_po_amount, 2)
        total_invoice_amount = round(total_invoice_amount, 2)
        total_variance_amount = round(total_variance_amount, 2)

        if has_critical_error:
            overall_status = MatchStatus.REJECTED
            is_payable = False
            summary = f"Conciliación 3 vías RECHAZADA. Se detectaron discrepancias graves en {sum(1 for f in findings if f.status == MatchStatus.REJECTED)} líneas."
        elif has_warning:
            overall_status = MatchStatus.FLAGGED
            is_payable = False
            summary = f"Conciliación 3 vías REQUIERE REVISIÓN. Variación total de {total_variance_amount:.2f}€ dentro de tolerancias operativas."
        else:
            overall_status = MatchStatus.APPROVED
            is_payable = True
            summary = f"Conciliación 3 vías APROBADA. Factura #{invoice_number} coincide al 100% con Pedido #{po_number} y Albarán."

        return ThreeWayMatchResult(
            status=overall_status,
            po_number=po_number,
            invoice_number=invoice_number,
            total_po_amount=total_po_amount,
            total_invoice_amount=total_invoice_amount,
            total_variance_amount=total_variance_amount,
            is_payable=is_payable,
            findings=findings,
            summary=summary,
        )
