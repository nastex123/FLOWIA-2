"""Documents list view with large Gothic KPI cards and anomaly badges."""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
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
from desktop.ui.styles import get_badge_qss

COLUMNS = [
    "Filename",
    "Estado",
    "Revision",
    "Severidad",
    "OK",
    "Warning",
    "Critical",
    "Info",
    "Creado",
]


class DocumentsView(QWidget):
    """Financial documents list with large KPI gothic cards and interactive filters."""

    document_activated = Signal(str)

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self._documents: List[Dict[str, Any]] = []
        self._active_filter: str = "all"
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Header Section
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("<h1 style='margin: 0; font-size: 24px; font-family: Georgia, serif; color: #fda4af; letter-spacing: 0.5px;'>Libro Mayor & Auditoria de Comprobantes</h1>")
        subtitle = QLabel("<span style='color: #a8a29e; font-size: 14px;'>Registro criptografico, deteccion de anomalias y analisis determinista de comprobantes</span>")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.refresh_btn = QPushButton("Actualizar Registros")
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.refresh_btn)
        layout.addLayout(header)

        # 2. Large Scale Gothic KPI Summary Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(14)

        self.total_card = self._create_kpi_card("TOTAL COMPROBANTES", "0", "#fda4af", "border-top: 3px solid #e11d48;")
        self.critical_card = self._create_kpi_card("ANOMALIAS CRITICAS", "0", "#fb7185", "border-top: 3px solid #be123c;")
        self.warning_card = self._create_kpi_card("ADVERTENCIAS FISCALES", "0", "#fde047", "border-top: 3px solid #d97706;")
        self.reviewed_card = self._create_kpi_card("CONSAGRADAS & AUDITADAS", "0", "#6ee7b7", "border-top: 3px solid #059669;")

        kpi_layout.addWidget(self.total_card)
        kpi_layout.addWidget(self.critical_card)
        kpi_layout.addWidget(self.warning_card)
        kpi_layout.addWidget(self.reviewed_card)
        layout.addLayout(kpi_layout)

        # 3. Search & Filter Bar (Gothic Frame)
        filter_frame = QFrame()
        filter_frame.setObjectName("glassCard")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Buscar por nombre de archivo, proveedor, NIF o estado...")
        self.search_edit.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.search_edit, stretch=2)

        # Chip Filters
        self.chip_all = QPushButton("Todos")
        self.chip_all.setObjectName("chipFilter")
        self.chip_all.setProperty("active", "true")
        self.chip_all.clicked.connect(lambda: self._set_chip_filter("all"))

        self.chip_critical = QPushButton("Criticos")
        self.chip_critical.setObjectName("chipFilter")
        self.chip_critical.clicked.connect(lambda: self._set_chip_filter("critical"))

        self.chip_warning = QPushButton("Advertencias")
        self.chip_warning.setObjectName("chipFilter")
        self.chip_warning.clicked.connect(lambda: self._set_chip_filter("warning"))

        self.chip_reviewed = QPushButton("Revisados")
        self.chip_reviewed.setObjectName("chipFilter")
        self.chip_reviewed.clicked.connect(lambda: self._set_chip_filter("reviewed"))

        self.chips = [self.chip_all, self.chip_critical, self.chip_warning, self.chip_reviewed]
        for chip in self.chips:
            filter_layout.addWidget(chip)

        layout.addWidget(filter_frame)

        # 4. Pro Table View (Crypt Theme)
        table_frame = QFrame()
        table_frame.setObjectName("glassPanel")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(4, 4, 4, 4)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(44)  # 44px Row Height
        self.table.doubleClicked.connect(self._on_double_clicked)
        self.model = VirtualDataTableModel()
        self.table.setModel(self.model)
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

        # 5. Bottom Status
        self.status_label = QLabel("<span style='color: #78716c; font-size: 13px;'>Cargando manuscritos y comprobantes...</span>")
        layout.addWidget(self.status_label)

    def _create_kpi_card(self, title: str, initial_value: str, color_hex: str, extra_border: str) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setStyleSheet(f"QFrame#kpiCard {{ {extra_border} }}")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(4)

        t_lbl = QLabel(f"<span style='color: #a8a29e; font-family: Georgia, serif; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;'>{title}</span>")
        v_lbl = QLabel(f"<b style='font-size: 32px; font-family: Georgia, serif; color: {color_hex}; line-height: 1.1;'>{initial_value}</b>")
        vbox.addWidget(t_lbl)
        vbox.addWidget(v_lbl)

        card._val_label = v_lbl
        card._color_hex = color_hex
        return card

    def _set_chip_filter(self, filter_type: str) -> None:
        self._active_filter = filter_type
        for chip in self.chips:
            is_active = (
                (chip == self.chip_all and filter_type == "all")
                or (chip == self.chip_critical and filter_type == "critical")
                or (chip == self.chip_warning and filter_type == "warning")
                or (chip == self.chip_reviewed and filter_type == "reviewed")
            )
            chip.setProperty("active", "true" if is_active else "false")
            chip.style().unpolish(chip)
            chip.style().polish(chip)
        self._apply_filter()

    def refresh(self) -> None:
        try:
            documents = self.client.list_documents()
        except FlowMindApiError as e:
            self.status_label.setText(f"<span style='color: #ef4444;'>Error cargando comprobantes: {e.detail}</span>")
            return
        self.set_documents(documents)

    def set_documents(self, documents: List[Dict[str, Any]]) -> None:
        self._documents = documents

        # Update KPIs
        total = len(documents)
        critical = sum(1 for d in documents if (d.get("check_summary") or {}).get("critical", 0) > 0)
        warning = sum(1 for d in documents if (d.get("check_summary") or {}).get("warning", 0) > 0)
        reviewed = sum(1 for d in documents if (d.get("review_status") or "") == "reviewed")

        self.total_card._val_label.setText(f"<b style='font-size: 32px; color: {self.total_card._color_hex};'>{total}</b>")
        self.critical_card._val_label.setText(f"<b style='font-size: 32px; color: {self.critical_card._color_hex};'>{critical}</b>")
        self.warning_card._val_label.setText(f"<b style='font-size: 32px; color: {self.warning_card._color_hex};'>{warning}</b>")
        self.reviewed_card._val_label.setText(f"<b style='font-size: 32px; color: {self.reviewed_card._color_hex};'>{reviewed}</b>")

        self.status_label.setText(f"<span style='color: #a8a29e;'>Mostrando {total} comprobantes procesados en la cripta</span>")
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_edit.text().strip().lower() if hasattr(self, "search_edit") else ""

        filtered = []
        for d in self._documents:
            text_match = not query or (
                query in d.get("filename", "").lower()
                or query in d.get("status", "").lower()
                or query in str(d.get("metadata", {})).lower()
            )
            if not text_match:
                continue

            summary = d.get("check_summary") or {}
            if self._active_filter == "critical" and int(summary.get("critical", 0)) == 0:
                continue
            if self._active_filter == "warning" and int(summary.get("warning", 0)) == 0:
                continue
            if self._active_filter == "reviewed" and (d.get("review_status") or "") != "reviewed":
                continue

            filtered.append(d)

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
        created = (document.get("created_at") or "")[:19].replace("T", " ")
        return {
            "Filename": document.get("filename", ""),
            "Estado": document.get("status", "").upper(),
            "Revision": (document.get("review_status") or "PENDIENTE").upper(),
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