"""Structured invoice review view with modern glassmorphism tabbed workspace."""

import json
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError
from desktop.models.table_model import VirtualDataTableModel
from desktop.ui.styles import get_badge_qss

ITEM_COLUMNS = ["Descripcion del Producto / Servicio", "Cantidad", "Precio Unitario", "% IVA", "Importe Total"]


class InvoiceReviewView(QWidget):
    """Full-screen tabbed review interface with glassmorphism aesthetics and floating action bar."""

    back_requested = Signal()
    review_completed = Signal(str)

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self._document_id: Optional[str] = None
        self._reviewed = False
        self._document_data: Dict[str, Any] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # 1. Top Header Bar
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("Volver a Facturas")
        self.back_btn.setObjectName("secondaryButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(self.back_btn)

        self.doc_title_label = QLabel("<b style='font-size: 18px; color: #f8fafc;'>Revision de Comprobante</b>")
        top_bar.addWidget(self.doc_title_label)

        self.severity_pill = QLabel("ESTADO: PENDIENTE")
        self.severity_pill.setStyleSheet(get_badge_qss("warning"))
        top_bar.addWidget(self.severity_pill)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 2. Main Glass Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("glassTabs")

        # TAB 1: Cabecera & Resumen
        self.tab_header = self._build_header_tab()
        self.tabs.addTab(self.tab_header, "Resumen & Cabecera")

        # TAB 2: Lineas de Items
        self.tab_items = self._build_items_tab()
        self.tabs.addTab(self.tab_items, "Lineas de Items")

        # TAB 3: Auditoria Sentinel (Antifraude)
        self.tab_sentinel = self._build_sentinel_tab()
        self.tabs.addTab(self.tab_sentinel, "Auditoria Sentinel")

        # TAB 4: Validador Matematico
        self.tab_math = self._build_math_tab()
        self.tabs.addTab(self.tab_math, "Validador Matematico")

        # TAB 5: JSON & Evidencia
        self.tab_json = self._build_json_tab()
        self.tabs.addTab(self.tab_json, "Evidencia & JSON")

        layout.addWidget(self.tabs, stretch=1)

        # 3. Bottom Floating Action Bar
        action_bar = QFrame()
        action_bar.setObjectName("actionBar")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(16, 12, 16, 12)

        self.action_status_label = QLabel("<span style='color: #94a3b8; font-size: 13px;'>Revisa los hallazgos y valida la exactitud antes de aprobar.</span>")
        action_layout.addWidget(self.action_status_label)
        action_layout.addStretch()

        self.review_btn = QPushButton("Aprobar y Marcar como Revisada")
        self.review_btn.setObjectName("successButton")
        self.review_btn.clicked.connect(self._on_review)
        self.review_btn.setEnabled(False)
        action_layout.addWidget(self.review_btn)

        layout.addWidget(action_bar)

    # ------------------------------------------------------------------
    # Tab Builders
    # ------------------------------------------------------------------

    def _build_header_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(14)

        # Row 1: Emisor & Receptor Cards
        row1 = QHBoxLayout()

        # Vendor Card
        vendor_card = QFrame()
        vendor_card.setObjectName("glassCard")
        v_layout = QVBoxLayout(vendor_card)
        v_layout.addWidget(QLabel("<b style='color: #38bdf8; font-size: 15px;'>EMISOR / PROVEEDOR</b>"))
        v_grid = QGridLayout()
        self.vendor_name_lbl = QLabel("—")
        self.vendor_tax_id_lbl = QLabel("—")
        self.vendor_iban_lbl = QLabel("—")
        self.vendor_address_lbl = QLabel("—")
        v_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Razon Social:</span>"), 0, 0)
        v_grid.addWidget(self.vendor_name_lbl, 0, 1)
        v_grid.addWidget(QLabel("<span style='color:#94a3b8;'>NIF / CIF:</span>"), 1, 0)
        v_grid.addWidget(self.vendor_tax_id_lbl, 1, 1)
        v_grid.addWidget(QLabel("<span style='color:#94a3b8;'>IBAN Bancario:</span>"), 2, 0)
        v_grid.addWidget(self.vendor_iban_lbl, 2, 1)
        v_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Direccion:</span>"), 3, 0)
        v_grid.addWidget(self.vendor_address_lbl, 3, 1)
        v_layout.addLayout(v_grid)
        row1.addWidget(vendor_card)

        # Customer Card
        customer_card = QFrame()
        customer_card.setObjectName("glassCard")
        c_layout = QVBoxLayout(customer_card)
        c_layout.addWidget(QLabel("<b style='color: #38bdf8; font-size: 15px;'>RECEPTOR / CLIENTE</b>"))
        c_grid = QGridLayout()
        self.customer_name_lbl = QLabel("—")
        self.customer_tax_id_lbl = QLabel("—")
        self.customer_address_lbl = QLabel("—")
        c_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Razon Social:</span>"), 0, 0)
        c_grid.addWidget(self.customer_name_lbl, 0, 1)
        c_grid.addWidget(QLabel("<span style='color:#94a3b8;'>NIF / CIF:</span>"), 1, 0)
        c_grid.addWidget(self.customer_tax_id_lbl, 1, 1)
        c_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Direccion:</span>"), 2, 0)
        c_grid.addWidget(self.customer_address_lbl, 2, 1)
        c_layout.addLayout(c_grid)
        row1.addWidget(customer_card)
        layout.addLayout(row1)

        # Row 2: Fechas & Metadatos
        meta_card = QFrame()
        meta_card.setObjectName("glassCard")
        m_layout = QVBoxLayout(meta_card)
        m_layout.addWidget(QLabel("<b style='color: #38bdf8; font-size: 15px;'>METADATOS DE FACTURA</b>"))
        m_grid = QGridLayout()
        self.inv_number_lbl = QLabel("—")
        self.issue_date_lbl = QLabel("—")
        self.due_date_lbl = QLabel("—")
        self.currency_lbl = QLabel("EUR")
        m_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Nº Factura:</span>"), 0, 0)
        m_grid.addWidget(self.inv_number_lbl, 0, 1)
        m_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Fecha Emision:</span>"), 0, 2)
        m_grid.addWidget(self.issue_date_lbl, 0, 3)
        m_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Vencimiento:</span>"), 1, 0)
        m_grid.addWidget(self.due_date_lbl, 1, 1)
        m_grid.addWidget(QLabel("<span style='color:#94a3b8;'>Divisa:</span>"), 1, 2)
        m_grid.addWidget(self.currency_lbl, 1, 3)
        m_layout.addLayout(m_grid)
        layout.addWidget(meta_card)

        # Row 3: Totales Financieros Destacados
        totals_card = QFrame()
        totals_card.setObjectName("glassCard")
        totals_card.setStyleSheet("QFrame#glassCard { background-color: rgba(30, 41, 59, 0.85); border: 2px solid rgba(56, 189, 248, 0.50); }")
        t_layout = QHBoxLayout(totals_card)
        t_layout.setContentsMargins(20, 16, 20, 16)

        self.subtotal_val = QLabel("0.00 EUR")
        self.subtotal_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        self.tax_val = QLabel("0.00 EUR")
        self.tax_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #fbbf24;")
        self.total_val = QLabel("0.00 EUR")
        self.total_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #34d399;")

        t_layout.addWidget(QLabel("<span style='color:#94a3b8;'>Subtotal Neto:<br></span>"))
        t_layout.addWidget(self.subtotal_val)
        t_layout.addStretch()
        t_layout.addWidget(QLabel("<span style='color:#94a3b8;'>Impuestos (IVA):<br></span>"))
        t_layout.addWidget(self.tax_val)
        t_layout.addStretch()
        t_layout.addWidget(QLabel("<span style='color:#94a3b8;'>TOTAL A PAGAR:<br></span>"))
        t_layout.addWidget(self.total_val)
        layout.addWidget(totals_card)

        scroll.setWidget(container)
        return scroll

    def _build_items_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        self.items_table = QTableView()
        self.items_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setDefaultSectionSize(44)
        self.items_model = VirtualDataTableModel()
        self.items_table.setModel(self.items_model)
        layout.addWidget(self.items_table)
        return widget

    def _build_sentinel_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        info_box = QLabel("<p style='color: #94a3b8; font-size: 13px;'>FlowMind Sentinel evalua riesgos de fraude: integridad de IBAN bancario, duplicidad documental cruzada y conformidad estadistica.</p>")
        layout.addWidget(info_box)

        self.sentinel_list = QListWidget()
        self.sentinel_list.setObjectName("glassPanel")
        layout.addWidget(self.sentinel_list)
        return widget

    def _build_math_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)

        card = QFrame()
        card.setObjectName("glassCard")
        c_layout = QVBoxLayout(card)
        c_layout.addWidget(QLabel("<b style='color: #38bdf8; font-size: 15px;'>VALIDACION ARITMETICA DETERMINISTA</b>"))

        self.math_summary_lbl = QLabel("<p style='color: #94a3b8;'>Recalculo automatico de bases imponibles y cuotas de impuestos.</p>")
        c_layout.addWidget(self.math_summary_lbl)

        self.math_diff_lbl = QLabel("<b>Estado:</b> —")
        c_layout.addWidget(self.math_diff_lbl)
        layout.addWidget(card)

        self.math_checks_list = QListWidget()
        self.math_checks_list.setObjectName("glassPanel")
        layout.addWidget(self.math_checks_list)
        return widget

    def _build_json_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.json_viewer = QTextEdit()
        self.json_viewer.setReadOnly(True)
        self.json_viewer.setFont(QFont("Consolas", 12))
        layout.addWidget(self.json_viewer)
        return widget

    # ------------------------------------------------------------------
    # Data Loading & Rendering
    # ------------------------------------------------------------------

    def load_document(self, document_id: str) -> None:
        """Loads a document detail and renders the structured invoice + findings."""
        self._document_id = document_id
        data = self.client.get_document(document_id)
        self._document_data = data
        invoice = data.get("structured_invoice") or {}
        checks = data.get("checks") or []
        self._reviewed = (data.get("review_status") or "") == "reviewed"
        self._render(invoice, checks, data)

    def _render(self, invoice: Dict[str, Any], checks: List[Dict[str, Any]], raw_doc: Dict[str, Any]) -> None:
        filename = raw_doc.get("filename", "Comprobante")
        self.doc_title_label.setText(f"<b style='font-size: 18px; color: #f8fafc;'>Revision: {filename}</b>")

        # Vendor Data
        self.vendor_name_lbl.setText(str(invoice.get("vendor_name") or "—"))
        self.vendor_tax_id_lbl.setText(str(invoice.get("vendor_tax_id") or "—"))
        self.vendor_iban_lbl.setText(str(invoice.get("vendor_iban") or "—"))
        self.vendor_address_lbl.setText(str(invoice.get("vendor_address") or "—"))

        # Customer Data
        self.customer_name_lbl.setText(str(invoice.get("customer_name") or "—"))
        self.customer_tax_id_lbl.setText(str(invoice.get("customer_tax_id") or "—"))
        self.customer_address_lbl.setText(str(invoice.get("customer_address") or "—"))

        # Metadata
        self.inv_number_lbl.setText(str(invoice.get("invoice_number") or "—"))
        self.issue_date_lbl.setText(str(invoice.get("issue_date") or "—"))
        self.due_date_lbl.setText(str(invoice.get("due_date") or "—"))
        curr = str(invoice.get("currency") or "EUR")
        self.currency_lbl.setText(curr)

        # Financial Totals
        def fmt(value: Any) -> str:
            return f"{float(value):,.2f} {curr}" if isinstance(value, (int, float)) else f"— {curr}"

        self.subtotal_val.setText(fmt(invoice.get("subtotal")))
        self.tax_val.setText(fmt(invoice.get("tax_total")))
        self.total_val.setText(fmt(invoice.get("total_amount")))

        # Items Table
        items = invoice.get("items") or []
        records = [
            {
                "Descripcion del Producto / Servicio": item.get("description", ""),
                "Cantidad": item.get("quantity", ""),
                "Precio Unitario": fmt(item.get("unit_price")),
                "% IVA": f"{item.get('tax_rate_pct', '')}%",
                "Importe Total": fmt(item.get("line_total")),
            }
            for item in items
        ]
        self.items_model.set_data(ITEM_COLUMNS, records)

        # Findings & Checks (Sentinel vs Math)
        self.sentinel_list.clear()
        self.math_checks_list.clear()

        has_critical = False
        has_warning = False

        for check in checks:
            severity = str(check.get("severity") or "info").lower()
            title = str(check.get("title") or check.get("check_type") or "Comprobacion")
            msg = str(check.get("message") or "")
            ctype = str(check.get("check_type") or "").lower()

            if severity == "critical":
                has_critical = True
            elif severity == "warning":
                has_warning = True

            item_text = f"[{severity.upper()}] {title}\n  - {msg}"
            list_item = QListWidgetItem(item_text)

            if "sentinel" in ctype or "iban" in ctype or "duplicate" in ctype:
                self.sentinel_list.addItem(list_item)
            else:
                self.math_checks_list.addItem(list_item)

        if self.sentinel_list.count() == 0:
            self.sentinel_list.addItem(QListWidgetItem("[OK] No se detectaron anomalias ni riesgos de fraude en Sentinel."))

        if self.math_checks_list.count() == 0:
            self.math_checks_list.addItem(QListWidgetItem("[OK] Los calculos aritmeticos coinciden con exactitud matematica."))

        # Severity Pill on Top Bar
        if self._reviewed:
            self.severity_pill.setText("REVISADA & APROBADA")
            self.severity_pill.setStyleSheet(get_badge_qss("ok"))
        elif has_critical:
            self.severity_pill.setText("ANOMALIA CRITICA")
            self.severity_pill.setStyleSheet(get_badge_qss("critical"))
        elif has_warning:
            self.severity_pill.setText("ADVERTENCIA")
            self.severity_pill.setStyleSheet(get_badge_qss("warning"))
        else:
            self.severity_pill.setText("VERIFICACION OK")
            self.severity_pill.setStyleSheet(get_badge_qss("ok"))

        # Raw JSON
        self.json_viewer.setPlainText(json.dumps(raw_doc, indent=2, ensure_ascii=False))

        # Review Button State
        self.review_btn.setEnabled(bool(self._document_id) and not self._reviewed)
        if self._reviewed:
            self.review_btn.setText("Comprobante Aprobado")
            self.action_status_label.setText("<span style='color: #34d399;'>Este comprobante ya fue auditado y marcado como revisado.</span>")
        else:
            self.review_btn.setText("Aprobar y Marcar como Revisada")
            self.action_status_label.setText("<span style='color: #94a3b8;'>Haz clic en Aprobar para guardar la auditoria en la base de datos.</span>")

    def _on_review(self) -> None:
        if not self._document_id:
            return
        note, ok = QInputDialog.getText(self, "Aprobar y Marcar como Revisada", "Nota o referencia de auditoria (opcional):")
        if not ok:
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar Aprobacion",
            "¿Confirmas que has revisado los importes e impuestos de este comprobante?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.client.review_document(self._document_id, note)
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error de revision", e.detail)
            return

        self._reviewed = True
        self.review_btn.setText("Comprobante Aprobado")
        self.review_btn.setEnabled(False)
        self.severity_pill.setText("REVISADA & APROBADA")
        self.severity_pill.setStyleSheet(get_badge_qss("ok"))
        QMessageBox.information(self, "Revision Exitosa", "El comprobante fue aprobado y marcado como revisado.")
        self.review_completed.emit(self._document_id)