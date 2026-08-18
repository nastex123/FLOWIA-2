"""Native PySide6 Desktop User Interface for FlowMind AI."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPalette
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QSystemTrayIcon,
    QTableView,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError
from desktop.models.table_model import VirtualDataTableModel
from desktop.services.tray_agent import HotFolderWatcher
from desktop.ui.documents_view import DocumentsView
from desktop.ui.invoice_review_view import InvoiceReviewView
from desktop.ui.login_dialog import LoginDialog
from desktop.ui.styles import DARK_THEME_QSS


class MainWindow(QMainWindow):
    """FlowMind AI Desktop Main Application Window (financial review app)."""

    def __init__(self, client: Optional[DesktopFlowMindClient] = None):
        super().__init__()
        self.setWindowTitle("FlowMind AI — Suite de Gestión Financiera & Auditoría")
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)

        self.client = client or DesktopFlowMindClient()
        self.hot_folder_watcher = HotFolderWatcher(on_processed=self._on_hot_folder_event)
        self.table_model = VirtualDataTableModel()
        self._document_id: Optional[str] = None
        self._settings_widget: Optional[QWidget] = None

        self._setup_modern_theme()
        self._init_ui()
        self._setup_tray_icon()

        QTimer.singleShot(0, self._prompt_login)

    def _setup_modern_theme(self) -> None:
        """Applies modern dark palette and centralized QSS."""
        self.setStyleSheet(DARK_THEME_QSS)

    def _init_ui(self) -> None:
        toolbar = QToolBar("Main Actions")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        login_action = QAction("🔐 Iniciar sesión", self)
        login_action.triggered.connect(self._prompt_login)
        toolbar.addAction(login_action)

        upload_action = QAction("⬆ Subir documento", self)
        upload_action.triggered.connect(self._upload_document)
        toolbar.addAction(upload_action)

        open_action = QAction("📂 Procesar localmente", self)
        open_action.triggered.connect(self._open_file_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        self.hotfolder_btn = QPushButton("▶ Activar Hot-Folder Agent")
        self.hotfolder_btn.setStyleSheet(
            "background-color: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;"
        )
        self.hotfolder_btn.clicked.connect(self._toggle_hot_folder)
        toolbar.addWidget(self.hotfolder_btn)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        for item in ("📄 Facturas", "📋 Detalle", "⚙️ Configuración", "🖥 Procesamiento Local"):
            self.sidebar.addItem(item)
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)
        main_layout.addWidget(self.sidebar)

        self.documents_view = DocumentsView(self.client)
        self.documents_view.document_activated.connect(self._open_document)

        self.invoice_review_view = InvoiceReviewView(self.client)
        self.invoice_review_view.back_requested.connect(self._go_to_documents)
        self.invoice_review_view.review_completed.connect(self._on_review_completed)

        self.placeholder_view = QLabel("Selecciona un comprobante en Facturas para revisarlo.")
        self.placeholder_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.settings_placeholder = QLabel("")
        self.settings_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.local_view = self._build_local_view()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.documents_view)  # 0 Facturas
        self.stack.addWidget(self.placeholder_view)  # 1 Detalle (inicial)
        self.stack.addWidget(self.settings_placeholder)  # 2 Configuración
        self.stack.addWidget(self.local_view)  # 3 Procesamiento Local
        main_layout.addWidget(self.stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo — Modo 100% Local (Zero Cloud Data Leakage)")

    def _build_local_view(self) -> QWidget:
        """Page preserving the original local extraction splitter view."""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("<b>Campos Clave Extraídos & Metadatos</b>"))
        self.fields_text = QTextEdit()
        self.fields_text.setReadOnly(True)
        self.fields_text.setPlaceholderText("Abre un archivo desde la barra para procesarlo localmente...")
        left_layout.addWidget(self.fields_text)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("<b>Vista de Tabla Estructurada (Reconciliation Grid)</b>"))
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table_view)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 750])

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(splitter)
        return wrapper

    def _setup_tray_icon(self) -> None:
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("FlowMind AI Desktop Agent")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_nav_changed(self, row: int) -> None:
        if row == 0:
            self.stack.setCurrentWidget(self.documents_view)
            self.documents_view.refresh()
        elif row == 1:
            if self._document_id:
                self.stack.setCurrentWidget(self.invoice_review_view)
            else:
                self.stack.setCurrentWidget(self.placeholder_view)
        elif row == 2:
            self._show_settings()
        elif row == 3:
            self.stack.setCurrentWidget(self.local_view)

    def _show_settings(self) -> None:
        if self._settings_widget is None:
            try:
                from desktop.ui.settings_view import SettingsView

                self._settings_widget = SettingsView(self.client)
            except ImportError:
                self._settings_widget = self.settings_placeholder
                self.settings_placeholder.setText(
                    "Configuración del Hot-Folder (SettingsView) se integrará en P4."
                )
            if self._settings_widget not in [self.stack.widget(i) for i in range(self.stack.count())]:
                self.stack.addWidget(self._settings_widget)
        self.stack.setCurrentWidget(self._settings_widget)

    def _go_to_documents(self) -> None:
        self.sidebar.setCurrentRow(0)

    def _open_document(self, document_id: str) -> None:
        try:
            self.invoice_review_view.load_document(document_id)
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error", e.detail)
            return
        self._document_id = document_id
        self.stack.setCurrentWidget(self.invoice_review_view)

    def _on_review_completed(self, document_id: str) -> None:
        self.documents_view.refresh()

    # ------------------------------------------------------------------
    # Authentication & upload
    # ------------------------------------------------------------------

    def _prompt_login(self) -> None:
        dialog = LoginDialog(self.client, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.documents_view.refresh()
            self.sidebar.setCurrentRow(0)
            self.status_bar.showMessage(
                f"Conectado a {self.client.base_url} — organización {self.client.organization_id}"
            )
        else:
            self.status_bar.showMessage("Sin autenticar — modo local disponible.")

    def _upload_document(self) -> None:
        file_filter = "Todos los compatibles (*.xlsx *.xls *.csv *.pdf *.png *.jpg *.jpeg);;Hojas de cálculo (*.xlsx *.xls *.csv);;PDFs (*.pdf);;Imágenes (*.png *.jpg *.jpeg)"
        path, _ = QFileDialog.getOpenFileName(self, "Subir documento al backend", "", file_filter)
        if not path:
            return
        try:
            result = self.client.upload_file(Path(path))
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error de subida", e.detail)
            return
        self.status_bar.showMessage(
            f"Documento {result.get('filename')} en cola ({result.get('status')})."
        )
        self.documents_view.refresh()

    # ------------------------------------------------------------------
    # Local processing (offline)
    # ------------------------------------------------------------------

    def _open_file_dialog(self) -> None:
        file_filter = "Todos los compatibles (*.xlsx *.xls *.csv *.pdf *.png *.jpg *.jpeg);;Hojas de cálculo (*.xlsx *.xls *.csv);;PDFs (*.pdf);;Imágenes (*.png *.jpg *.jpeg)"
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar documento de negocio", "", file_filter)
        if path:
            self.sidebar.setCurrentRow(3)
            self.process_file(Path(path))

    def process_file(self, file_path: Path) -> None:
        self.status_bar.showMessage(f"Procesando '{file_path.name}'...")
        try:
            res = self.client.process_file_locally(file_path)

            lines = [
                f"📄 Documento: {res.get('filename')}",
                f"🏷️ Clasificación: {res.get('classification', {}).get('document_type', 'unknown').upper()} "
                f"({int(res.get('classification', {}).get('confidence', 0) * 100)}%)",
                f"⏱️ Tiempo: {res.get('processing_time_ms', 0)} ms",
                "------------------------------------------------",
                "CAMPOS EXTRAÍDOS:",
            ]
            for k, f in res.get("fields", {}).items():
                lines.append(f" • {k}: {f.get('value')}  (conf: {f.get('confidence', 1.0):.2f})")

            self.fields_text.setPlainText("\n".join(lines))

            tables = res.get("tables", [])
            if tables:
                headers = tables[0].get("headers", [])
                records = tables[0].get("records", [])
                self.table_model.set_data(headers, records)
                self.status_bar.showMessage(
                    f"Completado en {res.get('processing_time_ms', 0)}ms — {len(records)} filas en tabla."
                )
            else:
                self.table_model.set_data([], [])
                self.status_bar.showMessage(
                    f"Completado en {res.get('processing_time_ms', 0)}ms — Sin tablas tabulares."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error de extracción", f"No se pudo procesar el archivo:\n{str(e)}")
            self.status_bar.showMessage("Error en procesamiento.")

    # ------------------------------------------------------------------
    # Hot-folder agent
    # ------------------------------------------------------------------

    def _toggle_hot_folder(self) -> None:
        if not self.hot_folder_watcher.is_running:
            self.hot_folder_watcher.start()
            self.hotfolder_btn.setText("⏹ Detener Hot-Folder Agent")
            self.hotfolder_btn.setStyleSheet(
                "background-color: #ef4444; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;"
            )
            self.status_bar.showMessage(f"Hot-Folder activo monitorizando: {self.hot_folder_watcher.input_dir}")
        else:
            self.hot_folder_watcher.stop()
            self.hotfolder_btn.setText("▶ Activar Hot-Folder Agent")
            self.hotfolder_btn.setStyleSheet(
                "background-color: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;"
            )
            self.status_bar.showMessage("Hot-Folder detenido.")

    def _on_hot_folder_event(self, filename: str, success: bool, message: str) -> None:
        self.status_bar.showMessage(f"[Hot-Folder] {filename}: {message}")