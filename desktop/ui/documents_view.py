"""Documents list view with anomaly badges for the FlowMind desktop app."""

from typing import Any, Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError
from desktop.models.table_model import VirtualDataTableModel

COLUMNS = [
    "Filename",
    "Estado",
    "Revisión",
    "Severidad",
    "OK",
    "Warning",
    "Critical",
    "Info",
    "Creado",
]


class DocumentsView(QWidget):
    """Financial documents list with severity badges and double-click to detail."""

    document_activated = Signal(str)

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self._documents: List[Dict[str, Any]] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("<h2>Facturas & Comprobantes</h2>")
        subtitle = QLabel("<span style='color: #94a3b8;'>Gestión de documentos procesados y auditoría de anomalías</span>")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        
        refresh_btn = QPushButton("⟳ Actualizar Lista")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # KPI Summary Row
        kpi_layout = QHBoxLayout()
        self.total_kpi = QLabel("<b>0</b><br><span style='color: #94a3b8; font-size: 11px;'>Total Documentos</span>")
        self.critical_kpi = QLabel("<b>0</b><br><span style='color: #ef4444; font-size: 11px;'>Anomalías Críticas</span>")
        self.warning_kpi = QLabel("<b>0</b><br><span style='color: #f59e0b; font-size: 11px;'>Advertencias</span>")
        self.reviewed_kpi = QLabel("<b>0</b><br><span style='color: #10b981; font-size: 11px;'>Revisadas</span>")
        for kpi in (self.total_kpi, self.critical_kpi, self.warning_kpi, self.reviewed_kpi):
            kpi.setObjectName("kpiCard")
            kpi.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 10px; font-size: 14px;")
            kpi_layout.addWidget(kpi)
        layout.addLayout(kpi_layout)

        # Filter bar
        filter_bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Buscar por nombre de archivo o estado...")
        self.search_edit.textChanged.connect(self._apply_filter)
        filter_bar.addWidget(self.search_edit)
        layout.addLayout(filter_bar)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self._on_double_clicked)
        self.model = VirtualDataTableModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def refresh(self) -> None:
        try:
            documents = self.client.list_documents()
        except FlowMindApiError as e:
            self.status_label.setText(f"Error cargando documentos: {e.detail}")
            return
        self.set_documents(documents)
        self.status_label.setText(f"{len(documents)} documentos")

    def set_documents(self, documents: List[Dict[str, Any]]) -> None:
        self._documents = documents
        
        # Update KPIs
        total = len(documents)
        critical = sum(1 for d in documents if (d.get("check_summary") or {}).get("critical", 0) > 0)
        warning = sum(1 for d in documents if (d.get("check_summary") or {}).get("warning", 0) > 0)
        reviewed = sum(1 for d in documents if (d.get("review_status") or "") == "reviewed")
        
        self.total_kpi.setText(f"<b>{total}</b><br><span style='color: #94a3b8; font-size: 11px;'>Total Documentos</span>")
        self.critical_kpi.setText(f"<b>{critical}</b><br><span style='color: #ef4444; font-size: 11px;'>Anomalías Críticas</span>")
        self.warning_kpi.setText(f"<b>{warning}</b><br><span style='color: #f59e0b; font-size: 11px;'>Advertencias</span>")
        self.reviewed_kpi.setText(f"<b>{reviewed}</b><br><span style='color: #10b981; font-size: 11px;'>Revisadas</span>")
        
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_edit.text().strip().lower() if hasattr(self, "search_edit") else ""
        filtered = [
            d for d in self._documents
            if not query or query in d.get("filename", "").lower() or query in d.get("status", "").lower()
        ]
        records = [self._to_record(d) for d in filtered]
        self.model.set_data(COLUMNS, records)
        self.model.set_severity_column(COLUMNS.index("Severidad"))

    @staticmethod
    def _to_record(document: Dict[str, Any]) -> Dict[str, Any]:
        summary = document.get("check_summary") or {}
        ok = int(summary.get("ok", 0))
        warning = int(summary.get("warning", 0))
        critical = int(summary.get("critical", 0))
        info = int(summary.get("info", 0))
        severity = "critical" if critical else ("warning" if warning else ("info" if info else "ok"))
        created = (document.get("created_at") or "")[:19]
        return {
            "Filename": document.get("filename", ""),
            "Estado": document.get("status", ""),
            "Revisión": document.get("review_status", ""),
            "Severidad": severity,
            "OK": ok,
            "Warning": warning,
            "Critical": critical,
            "Info": info,
            "Creado": created,
        }

    def _on_double_clicked(self, index) -> None:
        row = index.row()
        if 0 <= row < len(self._documents):
            self.document_activated.emit(self._documents[row].get("document_id", ""))