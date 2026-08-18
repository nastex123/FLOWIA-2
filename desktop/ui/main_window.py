"""Native PySide6 Desktop User Interface for FlowMind AI (Glassmorphism + Particle Canvas)."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
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
from desktop.ui.components.animations import PageTransitioner, SidebarAnimator
from desktop.ui.components.particle_backdrop import ParticleBackdropWidget
from desktop.ui.documents_view import DocumentsView
from desktop.ui.invoice_review_view import InvoiceReviewView
from desktop.ui.login_dialog import LoginDialog
from desktop.ui.styles import DARK_THEME_QSS, get_badge_qss


class MainWindow(QMainWindow):
    """FlowMind AI Desktop Main Application Window with Animated Ambient Background."""

    def __init__(self, client: Optional[DesktopFlowMindClient] = None):
        super().__init__()
        self.setWindowTitle("FlowMind AI — Suite de Gestion Financiera & Auditoria Local")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 720)

        self.client = client or DesktopFlowMindClient()
        self.hot_folder_watcher = HotFolderWatcher(on_processed=self._on_hot_folder_event)
        self.table_model = VirtualDataTableModel()
        self._document_id: Optional[str] = None
        self._settings_widget: Optional[QWidget] = None
        self._sidebar_expanded: bool = True

        self._setup_modern_theme()
        self._init_ui()
        self._setup_tray_icon()

        QTimer.singleShot(0, self._prompt_login)

    def _setup_modern_theme(self) -> None:
        """Applies modern dark palette and centralized QSS."""
        self.setStyleSheet(DARK_THEME_QSS)

    def _init_ui(self) -> None:
        # 1. Top Glass Header Bar
        toolbar = QToolBar("Acciones Principales")
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Brand / Title Label
        brand_label = QLabel("<b style='font-size: 16px; color: #38bdf8;'>FlowMind AI</b> &nbsp;<span style='color: #64748b;'>| Suite Desktop</span>")
        brand_label.setStyleSheet("padding-left: 8px; padding-right: 16px;")
        toolbar.addWidget(brand_label)

        login_action = QAction("Iniciar Sesion", self)
        login_action.triggered.connect(self._prompt_login)
        toolbar.addAction(login_action)

        upload_action = QAction("Subir Documento", self)
        upload_action.triggered.connect(self._upload_document)
        toolbar.addAction(upload_action)

        open_action = QAction("Extraer Localmente", self)
        open_action.triggered.connect(self._open_file_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        self.hotfolder_btn = QPushButton("Activar Hot-Folder")
        self.hotfolder_btn.setObjectName("secondaryButton")
        self.hotfolder_btn.clicked.connect(self._toggle_hot_folder)
        toolbar.addWidget(self.hotfolder_btn)

        # Spacer to push connection status to the right
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding, spacer.sizePolicy().verticalPolicy().Preferred)
        toolbar.addWidget(spacer)

        # Connection Status Pill
        self.conn_pill = QLabel("Modo Local")
        self.conn_pill.setStyleSheet(get_badge_qss("ok"))
        toolbar.addWidget(self.conn_pill)

        # 2. Central Layout Container with Particle Backdrop
        central_container = QWidget()
        self.setCentralWidget(central_container)

        # Particle Backdrop Canvas (bottom layer)
        self.particle_backdrop = ParticleBackdropWidget(num_particles=38, parent=central_container)

        # Foreground UI Layout
        main_layout = QHBoxLayout(central_container)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Ensure particle canvas resizes with central widget
        central_container.resizeEvent = self._handle_central_resize

        # 3. Sidebar Container (Glass Frame)
        self.sidebar_container = QWidget()
        self.sidebar_container.setObjectName("sidebarContainer")
        self.sidebar_container.setFixedWidth(240)
        self.sidebar_animator = SidebarAnimator(self.sidebar_container, duration_ms=240, parent=self)

        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(8)

        # Sidebar Header with Toggle Button
        sidebar_top = QHBoxLayout()
        self.sidebar_title = QLabel("<b style='color: #cbd5e1; font-size: 13px; letter-spacing: 0.5px;'>NAVEGACION</b>")
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setObjectName("sidebarToggle")
        self.toggle_btn.setToolTip("Plegar / Desplegar barra lateral")
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
        sidebar_top.addWidget(self.sidebar_title)
        sidebar_top.addStretch()
        sidebar_top.addWidget(self.toggle_btn)
        sidebar_layout.addLayout(sidebar_top)

        # Navigation List
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")

        self.nav_items_data = [
            ("Facturas & Auditoria", "FACT"),
            ("Revision Detallada", "REV"),
            ("Configuracion", "CONF"),
            ("Procesamiento Local", "LOC"),
        ]

        for full_text, _ in self.nav_items_data:
            item = QListWidgetItem(full_text)
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.sidebar)

        # Sidebar Footer
        self.sidebar_footer = QLabel("<div style='color: #475569; font-size: 11px; text-align: center;'>FlowMind AI v0.2.0<br>100% Local & Privado</div>")
        self.sidebar_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.sidebar_footer)

        main_layout.addWidget(self.sidebar_container)

        # 4. Main Stacked Views with Smooth Page Transitioner
        self.documents_view = DocumentsView(self.client)
        self.documents_view.document_activated.connect(self._open_document)

        self.invoice_review_view = InvoiceReviewView(self.client)
        self.invoice_review_view.back_requested.connect(self._go_to_documents)
        self.invoice_review_view.review_completed.connect(self._on_review_completed)

        self.placeholder_view = QFrame()
        self.placeholder_view.setObjectName("glassCard")
        ph_layout = QVBoxLayout(self.placeholder_view)
        ph_label = QLabel("<h3>Ningun comprobante seleccionado</h3><p style='color: #94a3b8;'>Ve a <b>Facturas & Auditoria</b> y haz doble clic sobre cualquier documento para abrir la inspeccion.</p>")
        ph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(ph_label)

        self.settings_placeholder = QFrame()
        self.settings_placeholder.setObjectName("glassCard")
        sph_layout = QVBoxLayout(self.settings_placeholder)
        self.settings_label = QLabel("<h3>Configuracion del Sistema</h3><p style='color: #94a3b8;'>El modulo de configuracion del agente Hot-Folder se integrara en P4.</p>")
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sph_layout.addWidget(self.settings_label)

        self.local_view = self._build_local_view()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.documents_view)       # 0 Facturas
        self.stack.addWidget(self.placeholder_view)     # 1 Detalle
        self.stack.addWidget(self.settings_placeholder) # 2 Configuracion
        self.stack.addWidget(self.local_view)           # 3 Procesamiento Local

        self.page_transitioner = PageTransitioner(self.stack, duration_ms=180, parent=self)
        main_layout.addWidget(self.stack)

        # 5. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo — Modo 100% Local y Privado (Zero Cloud Data Leakage)")

    def _handle_central_resize(self, event) -> None:
        if hasattr(self, "particle_backdrop"):
            self.particle_backdrop.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
        QWidget.resizeEvent(self.centralWidget(), event)

    def _toggle_sidebar(self) -> None:
        """Smoothly animates sidebar between expanded (240px) and collapsed (68px)."""
        self._sidebar_expanded = not self._sidebar_expanded
        target_w = 240 if self._sidebar_expanded else 68
        self.sidebar_animator.animate_to(target_w)

        if self._sidebar_expanded:
            self.sidebar_title.show()
            self.sidebar_footer.show()
            self.toggle_btn.setText("≡")
            for i, (full_text, _) in enumerate(self.nav_items_data):
                item = self.sidebar.item(i)
                if item:
                    item.setText(full_text)
                    item.setToolTip("")
        else:
            self.sidebar_title.hide()
            self.sidebar_footer.hide()
            self.toggle_btn.setText("▶")
            for i, (full_text, icon_only) in enumerate(self.nav_items_data):
                item = self.sidebar.item(i)
                if item:
                    item.setText(icon_only)
                    item.setToolTip(full_text)

    def _build_local_view(self) -> QWidget:
        """Splitter view for instant local extraction without backend."""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QFrame()
        left_widget.setObjectName("glassCard")
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("<b>Campos Clave Extraidos & Metadatos Locales</b>"))
        self.fields_text = QTextEdit()
        self.fields_text.setReadOnly(True)
        self.fields_text.setPlaceholderText("Abre un archivo desde la barra de herramientas para procesarlo con los motores locales...")
        left_layout.addWidget(self.fields_text)
        splitter.addWidget(left_widget)

        right_widget = QFrame()
        right_widget.setObjectName("glassCard")
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("<b>Vista de Tabla Estructurada (Reconciliation Grid Pro)</b>"))
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table_view)
        splitter.addWidget(right_widget)

        splitter.setSizes([500, 800])

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
            self.page_transitioner.transition_to_widget(self.documents_view)
            self.documents_view.refresh()
        elif row == 1:
            target = self.invoice_review_view if self._document_id else self.placeholder_view
            self.page_transitioner.transition_to_widget(target)
        elif row == 2:
            self._show_settings()
        elif row == 3:
            self.page_transitioner.transition_to_widget(self.local_view)

    def _show_settings(self) -> None:
        if self._settings_widget is None:
            try:
                from desktop.ui.settings_view import SettingsView

                self._settings_widget = SettingsView(self.client)
            except ImportError:
                self._settings_widget = self.settings_placeholder
                self.settings_label.setText(
                    "<h3>Configuracion del Hot-Folder</h3><p style='color: #94a3b8;'>El modulo `SettingsView` se integrara en P4.</p>"
                )
            if self._settings_widget not in [self.stack.widget(i) for i in range(self.stack.count())]:
                self.stack.addWidget(self._settings_widget)
        self.page_transitioner.transition_to_widget(self._settings_widget)

    def _go_to_documents(self) -> None:
        self.sidebar.setCurrentRow(0)

    def _open_document(self, document_id: str) -> None:
        try:
            self.invoice_review_view.load_document(document_id)
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error", e.detail)
            return
        self._document_id = document_id
        self.page_transitioner.transition_to_widget(self.invoice_review_view)
        self.sidebar.setCurrentRow(1)

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
            org = self.client.organization_id or "default-org"
            self.conn_pill.setText(f"Conectado ({org})")
            self.conn_pill.setStyleSheet(get_badge_qss("ok"))
            self.status_bar.showMessage(
                f"Conectado a {self.client.base_url} — Org: {org}"
            )
        else:
            self.conn_pill.setText("Modo Offline")
            self.conn_pill.setStyleSheet(get_badge_qss("warning"))
            self.status_bar.showMessage("Sin autenticar — Modo Demo / Extraccion Local activo.")

    def _upload_document(self) -> None:
        file_filter = "Todos los compatibles (*.xlsx *.xls *.csv *.pdf *.png *.jpg *.jpeg);;Hojas de calculo (*.xlsx *.xls *.csv);;PDFs (*.pdf);;Imagenes (*.png *.jpg *.jpeg)"
        path, _ = QFileDialog.getOpenFileName(self, "Subir documento al backend", "", file_filter)
        if not path:
            return
        try:
            result = self.client.upload_file(Path(path))
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error de subida", e.detail)
            return
        self.status_bar.showMessage(
            f"Documento '{result.get('filename')}' enviado a la cola ({result.get('status')})."
        )
        self.documents_view.refresh()

    # ------------------------------------------------------------------
    # Local processing (offline)
    # ------------------------------------------------------------------

    def _open_file_dialog(self) -> None:
        file_filter = "Todos los compatibles (*.xlsx *.xls *.csv *.pdf *.png *.jpg *.jpeg);;Hojas de calculo (*.xlsx *.xls *.csv);;PDFs (*.pdf);;Imagenes (*.png *.jpg *.jpeg)"
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar documento de negocio", "", file_filter)
        if path:
            self.sidebar.setCurrentRow(3)
            self.process_file(Path(path))

    def process_file(self, file_path: Path) -> None:
        self.status_bar.showMessage(f"Extrayendo y clasificando '{file_path.name}'...")
        try:
            res = self.client.process_file_locally(file_path)

            lines = [
                f"Documento: {res.get('filename')}",
                f"Clasificacion: {res.get('classification', {}).get('document_type', 'unknown').upper()} "
                f"({int(res.get('classification', {}).get('confidence', 0) * 100)}%)",
                f"Tiempo de Inferencia: {res.get('processing_time_ms', 0)} ms",
                "================================================",
                "CAMPOS EXTRAIDOS E IDENTIFICADOS:",
            ]
            for k, f in res.get("fields", {}).items():
                lines.append(f" - {k}: {f.get('value')}  (confianza: {f.get('confidence', 1.0):.2f})")

            self.fields_text.setPlainText("\n".join(lines))

            tables = res.get("tables", [])
            if tables:
                headers = tables[0].get("headers", [])
                records = tables[0].get("records", [])
                self.table_model.set_data(headers, records)
                self.status_bar.showMessage(
                    f"Extraccion completada en {res.get('processing_time_ms', 0)}ms — {len(records)} filas procesadas."
                )
            else:
                self.table_model.set_data([], [])
                self.status_bar.showMessage(
                    f"Extraccion completada en {res.get('processing_time_ms', 0)}ms — Sin tablas detectadas."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error de extraccion", f"No se pudo procesar el archivo:\n{str(e)}")
            self.status_bar.showMessage("Error en procesamiento local.")

    # ------------------------------------------------------------------
    # Hot-folder agent
    # ------------------------------------------------------------------

    def _toggle_hot_folder(self) -> None:
        if not self.hot_folder_watcher.is_running:
            self.hot_folder_watcher.start()
            self.hotfolder_btn.setText("Detener Hot-Folder")
            self.hotfolder_btn.setStyleSheet(
                "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #b91c1c); color: white; font-weight: bold; border-color: rgba(239, 68, 68, 0.6);"
            )
            self.status_bar.showMessage(f"Hot-Folder activo monitorizando: {self.hot_folder_watcher.input_dir}")
        else:
            self.hot_folder_watcher.stop()
            self.hotfolder_btn.setText("Activar Hot-Folder")
            self.hotfolder_btn.setStyleSheet("")
            self.status_bar.showMessage("Hot-Folder detenido.")

    def _on_hot_folder_event(self, filename: str, success: bool, message: str) -> None:
        self.status_bar.showMessage(f"[Hot-Folder] {filename}: {message}")