"""Structured invoice review view: header, items, taxes, findings and review action."""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError
from desktop.models.table_model import VirtualDataTableModel

SEVERITY_COLORS = {
    "ok": QColor("#22c55e"),
    "warning": QColor("#f59e0b"),
    "critical": QColor("#ef4444"),
    "info": QColor("#3b82f6"),
    "unknown": QColor("#94a3b8"),
}

ITEM_COLUMNS = ["Descripción", "Cantidad", "Precio unitario", "% IVA", "Importe línea"]


class InvoiceReviewView(QWidget):
    """Displays a structured invoice, its findings and the review action."""

    back_requested = Signal()
    review_completed = Signal(str)

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self._document_id: Optional[str] = None
        self._reviewed = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header Bar with Back and Review actions
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Volver a Facturas")
        back_btn.setStyleSheet("background-color: #1f2937; color: #f1f5f9;")
        back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        self.review_btn = QPushButton("✓ Marcar como revisada")
        self.review_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 8px 16px;")
        self.review_btn.clicked.connect(self._on_review)
        self.review_btn.setEnabled(False)
        top_bar.addWidget(self.review_btn)
        layout.addLayout(top_bar)

        # Splitter with 2 main columns
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Column: Invoice Details & Items
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        header_frame = QWidget()
        header_frame.setObjectName("card")
        header_grid = QGridLayout(header_frame)
        header_grid.setContentsMargins(12, 12, 12, 12)
        header_grid.setSpacing(8)

        self.vendor_label = QLabel("—")
        self.tax_id_label = QLabel("—")
        self.invoice_number_label = QLabel("—")
        self.issue_label = QLabel("—")
        self.due_label = QLabel("—")
        self.currency_label = QLabel("—")
        self.customer_label = QLabel("—")
        for row, (name, widget) in enumerate(
            [
                ("Proveedor", self.vendor_label),
                ("NIF/CIF", self.tax_id_label),
                ("Nº Factura", self.invoice_number_label),
                ("Emisión", self.issue_label),
                ("Vencimiento", self.due_label),
                ("Divisa", self.currency_label),
                ("Cliente", self.customer_label),
            ]
        ):
            label = QLabel(f"<span style='color: #94a3b8;'>{name}:</span>")
            header_grid.addWidget(label, row // 2, (row % 2) * 2, Qt.AlignmentFlag.AlignRight)
            header_grid.addWidget(widget, row // 2, (row % 2) * 2 + 1)
        left_layout.addWidget(header_frame)

        left_layout.addWidget(QLabel("<b>Ítems de la Factura</b>"))
        self.items_table = QTableView()
        self.items_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_model = VirtualDataTableModel()
        self.items_table.setModel(self.items_model)
        left_layout.addWidget(self.items_table)

        summary_frame = QWidget()
        summary_frame.setObjectName("card")
        summary = QHBoxLayout(summary_frame)
        summary.setContentsMargins(12, 12, 12, 12)

        self.subtotal_label = QLabel("<b>—</b>")
        self.tax_label = QLabel("<b>—</b>")
        self.total_label = QLabel("<b>—</b>")
        for name, widget in [("Subtotal:", self.subtotal_label), ("Impuestos (IVA):", self.tax_label), ("Total Factura:", self.total_label)]:
            summary.addWidget(QLabel(f"<span style='color: #94a3b8;'>{name}</span>"))
            summary.addWidget(widget)
            summary.addStretch()
        left_layout.addWidget(summary_frame)
        splitter.addWidget(left_widget)

        # Right Column: Findings & Audit Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        right_layout.addWidget(QLabel("<b>Hallazgos de Auditoría (Document Checks)</b>"))
        self.checks_list = QListWidget()
        right_layout.addWidget(self.checks_list)
        splitter.addWidget(right_widget)

        splitter.setSizes([750, 450])
        layout.addWidget(splitter)

    def load_document(self, document_id: str) -> None:
        """Loads a document detail and renders the structured invoice + findings."""
        self._document_id = document_id
        data = self.client.get_document(document_id)
        invoice = data.get("structured_invoice") or {}
        checks = data.get("checks") or []
        self._reviewed = (data.get("review_status") or "") == "reviewed"
        self._render(invoice, checks)

    def _render(self, invoice: Dict[str, Any], checks: List[Dict[str, Any]]) -> None:
        self.vendor_label.setText(str(invoice.get("vendor_name") or "—"))
        self.tax_id_label.setText(str(invoice.get("vendor_tax_id") or "—"))
        self.invoice_number_label.setText(str(invoice.get("invoice_number") or "—"))
        self.issue_label.setText(str(invoice.get("issue_date") or "—"))
        self.due_label.setText(str(invoice.get("due_date") or "—"))
        self.currency_label.setText(str(invoice.get("currency") or "—"))
        self.customer_label.setText(str(invoice.get("customer_name") or "—"))

        items = invoice.get("items") or []
        records = [
            {
                "Descripción": item.get("description", ""),
                "Cantidad": item.get("quantity", ""),
                "Precio unitario": item.get("unit_price", ""),
                "% IVA": item.get("tax_rate_pct", ""),
                "Importe línea": item.get("line_total", ""),
            }
            for item in items
        ]
        self.items_model.set_data(ITEM_COLUMNS, records)

        def fmt(value: Any) -> str:
            return f"{float(value):.2f}" if isinstance(value, (int, float)) else "—"

        self.subtotal_label.setText(fmt(invoice.get("subtotal")))
        self.tax_label.setText(fmt(invoice.get("tax_total")))
        self.total_label.setText(fmt(invoice.get("total_amount")))

        self.checks_list.clear()
        for check in checks:
            severity = str(check.get("severity") or "unknown").lower()
            title = str(check.get("title") or check.get("check_type") or "sin título")
            item = QListWidgetItem(f"[{severity.upper()}] {title}")
            item.setForeground(SEVERITY_COLORS.get(severity, SEVERITY_COLORS["unknown"]))
            self.checks_list.addItem(item)

        self.review_btn.setEnabled(bool(self._document_id) and not self._reviewed)
        self.review_btn.setText("Marcar como revisada" if not self._reviewed else "Revisada ✓")

    def _on_review(self) -> None:
        if not self._document_id:
            return
        note, ok = QInputDialog.getText(self, "Marcar como revisada", "Nota (opcional):")
        if not ok:
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar revisión",
            "¿Marcar este comprobante como revisado?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.client.review_document(self._document_id, note)
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error de revisión", e.detail)
            return
        self._reviewed = True
        self.review_btn.setText("Revisada ✓")
        self.review_btn.setEnabled(False)
        QMessageBox.information(self, "Revisión completada", "El comprobante quedó marcado como revisado.")
        self.review_completed.emit(self._document_id)