"""Settings view for the FlowMind AI Hot-Folder agent configuration."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient
from desktop.services.tray_agent import HotFolderWatcher


class SettingsView(QWidget):
    """Configuration screen for the Hot-Folder background agent.

    Allows the user to:
    - Set the input/output folder paths for the hot-folder watcher.
    - Enter the API Key (fm_...) used to authenticate uploads to the backend.
    - Enter the Organization ID for multi-tenant routing.
    - Start / stop the hot-folder watcher.
    - View a real-time activity log of processed files.
    """

    # Emitted when the agent status changes: (is_running: bool)
    agent_status_changed = Signal(bool)

    def __init__(
        self,
        client: Optional[DesktopFlowMindClient] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.client = client or DesktopFlowMindClient()
        self._watcher: Optional[HotFolderWatcher] = None

        self._build_ui()
        self._sync_from_client()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # Page title
        title = QLabel(
            "<h2 style='font-family: Georgia, serif; color: #fda4af; letter-spacing: 1px;'>"
            "Configuracion del Agente</h2>"
            "<p style='color: #64748b; font-size: 13px;'>"
            "Ajusta el Hot-Folder, la clave de API y la organizacion para la automatizacion de comprobantes.</p>"
        )
        title.setWordWrap(True)
        root.addWidget(title)

        # ---- Group: Backend connection ----
        conn_group = QGroupBox("Conexion al Backend")
        conn_group.setStyleSheet(
            "QGroupBox { border: 1px solid rgba(136,19,55,0.40); border-radius: 8px;"
            " padding: 14px; margin-top: 10px; color: #fda4af; font-family: Georgia, serif; font-weight: bold; }"
            " QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; }"
        )
        conn_layout = QVBoxLayout(conn_group)
        conn_layout.setSpacing(10)

        # API Key row
        api_key_row = QHBoxLayout()
        api_key_label = QLabel("API Key (fm_...):")
        api_key_label.setFixedWidth(160)
        api_key_label.setStyleSheet("color: #94a3b8;")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("fm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_key_btn = QPushButton("Mostrar")
        self.show_key_btn.setObjectName("secondaryButton")
        self.show_key_btn.setFixedWidth(80)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self._toggle_api_key_visibility)
        api_key_row.addWidget(api_key_label)
        api_key_row.addWidget(self.api_key_edit)
        api_key_row.addWidget(self.show_key_btn)
        conn_layout.addLayout(api_key_row)

        # Organization ID row
        org_row = QHBoxLayout()
        org_label = QLabel("Organizacion ID:")
        org_label.setFixedWidth(160)
        org_label.setStyleSheet("color: #94a3b8;")
        self.org_edit = QLineEdit()
        self.org_edit.setPlaceholderText("default-org")
        org_row.addWidget(org_label)
        org_row.addWidget(self.org_edit)
        conn_layout.addLayout(org_row)

        # Backend URL row
        url_row = QHBoxLayout()
        url_label = QLabel("URL del Backend:")
        url_label.setFixedWidth(160)
        url_label.setStyleSheet("color: #94a3b8;")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("http://127.0.0.1:8000")
        url_row.addWidget(url_label)
        url_row.addWidget(self.url_edit)
        conn_layout.addLayout(url_row)

        root.addWidget(conn_group)

        # ---- Group: Hot-Folder paths ----
        folder_group = QGroupBox("Carpetas del Hot-Folder")
        folder_group.setStyleSheet(
            "QGroupBox { border: 1px solid rgba(136,19,55,0.40); border-radius: 8px;"
            " padding: 14px; margin-top: 10px; color: #fda4af; font-family: Georgia, serif; font-weight: bold; }"
            " QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; }"
        )
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(10)

        # Input folder row
        input_row = QHBoxLayout()
        input_label = QLabel("Carpeta de entrada:")
        input_label.setFixedWidth(160)
        input_label.setStyleSheet("color: #94a3b8;")
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("Ruta de la carpeta monitorizada...")
        self.input_dir_edit.setReadOnly(True)
        browse_input_btn = QPushButton("Examinar")
        browse_input_btn.setObjectName("secondaryButton")
        browse_input_btn.setFixedWidth(90)
        browse_input_btn.clicked.connect(self._browse_input_dir)
        input_row.addWidget(input_label)
        input_row.addWidget(self.input_dir_edit)
        input_row.addWidget(browse_input_btn)
        folder_layout.addLayout(input_row)

        # Output folder row
        output_row = QHBoxLayout()
        output_label = QLabel("Carpeta de salida:")
        output_label.setFixedWidth(160)
        output_label.setStyleSheet("color: #94a3b8;")
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Ruta donde se guardan los JSON extraidos...")
        self.output_dir_edit.setReadOnly(True)
        browse_output_btn = QPushButton("Examinar")
        browse_output_btn.setObjectName("secondaryButton")
        browse_output_btn.setFixedWidth(90)
        browse_output_btn.clicked.connect(self._browse_output_dir)
        output_row.addWidget(output_label)
        output_row.addWidget(self.output_dir_edit)
        output_row.addWidget(browse_output_btn)
        folder_layout.addLayout(output_row)

        root.addWidget(folder_group)

        # ---- Action buttons ----
        action_bar = QFrame()
        action_bar.setObjectName("actionBar")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(12)

        self.save_btn = QPushButton("Guardar configuracion")
        self.save_btn.clicked.connect(self._save_config)

        self.start_btn = QPushButton("Iniciar agente")
        self.start_btn.setObjectName("successButton")
        self.start_btn.clicked.connect(self._start_agent)

        self.stop_btn = QPushButton("Detener agente")
        self.stop_btn.setObjectName("secondaryButton")
        self.stop_btn.clicked.connect(self._stop_agent)
        self.stop_btn.setEnabled(False)

        action_layout.addWidget(self.save_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.stop_btn)

        root.addWidget(action_bar)

        # ---- Activity log ----
        log_group = QGroupBox("Registro de Actividad del Agente")
        log_group.setStyleSheet(
            "QGroupBox { border: 1px solid rgba(136,19,55,0.40); border-radius: 8px;"
            " padding: 14px; margin-top: 10px; color: #fda4af; font-family: Georgia, serif; font-weight: bold; }"
            " QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; }"
        )
        log_layout = QVBoxLayout(log_group)

        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setPlaceholderText("Los eventos del agente aparecen aqui una vez que el hot-folder este activo...")
        self.log_widget.setMinimumHeight(160)
        self.log_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        log_layout.addWidget(self.log_widget)

        clear_log_btn = QPushButton("Limpiar registro")
        clear_log_btn.setObjectName("secondaryButton")
        clear_log_btn.setFixedWidth(140)
        clear_log_btn.clicked.connect(self.log_widget.clear)
        log_layout.addWidget(clear_log_btn, alignment=Qt.AlignmentFlag.AlignRight)

        root.addWidget(log_group)

        # Status indicator at the bottom
        self.status_label = QLabel("Estado del agente: <b style='color: #64748b;'>Inactivo</b>")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 4px 0;")
        root.addWidget(self.status_label)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _sync_from_client(self) -> None:
        """Populates the form fields from the current client configuration."""
        if self.client.api_key:
            self.api_key_edit.setText(self.client.api_key)
        if self.client.organization_id:
            self.org_edit.setText(self.client.organization_id)
        self.url_edit.setText(self.client.base_url)

        # Pre-fill default hot-folder paths
        base = Path.cwd() / "hot_folder"
        self.input_dir_edit.setText(str(base / "in"))
        self.output_dir_edit.setText(str(base / "out"))

    def _toggle_api_key_visibility(self, checked: bool) -> None:
        if checked:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("Ocultar")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("Mostrar")

    def _browse_input_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de entrada del Hot-Folder"
        )
        if path:
            self.input_dir_edit.setText(path)

    def _browse_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de salida del Hot-Folder"
        )
        if path:
            self.output_dir_edit.setText(path)

    def _save_config(self) -> None:
        """Persists the form values into the shared client instance."""
        api_key = self.api_key_edit.text().strip()
        org_id = self.org_edit.text().strip() or "default-org"
        backend_url = self.url_edit.text().strip() or "http://127.0.0.1:8000"

        self.client.api_key = api_key if api_key else None
        self.client.organization_id = org_id
        self.client.base_url = backend_url.rstrip("/")

        self._append_log("Configuracion guardada correctamente.")
        self.status_label.setText(
            "Estado del agente: <b style='color: #34d399;'>Configuracion aplicada</b>"
        )

    def _start_agent(self) -> None:
        """Saves the config and starts the HotFolderWatcher."""
        self._save_config()

        input_dir = Path(self.input_dir_edit.text().strip())
        output_dir = Path(self.output_dir_edit.text().strip())

        if self._watcher and self._watcher.is_running:
            self._append_log("El agente ya esta en ejecucion.")
            return

        self._watcher = HotFolderWatcher(
            input_dir=input_dir,
            output_dir=output_dir,
            on_processed=self._on_file_processed,
        )
        # Inject the configured client so the watcher uses the API Key
        self._watcher.client = self.client

        self._watcher.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(
            f"Estado del agente: <b style='color: #34d399;'>Activo</b> — monitorizando {input_dir}"
        )
        self._append_log(f"Agente iniciado. Monitorizando: {input_dir}")
        self.agent_status_changed.emit(True)

    def _stop_agent(self) -> None:
        """Stops the running HotFolderWatcher."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(
            "Estado del agente: <b style='color: #64748b;'>Inactivo</b>"
        )
        self._append_log("Agente detenido.")
        self.agent_status_changed.emit(False)

    def _on_file_processed(self, filename: str, success: bool, message: str) -> None:
        """Callback invoked by HotFolderHandler after processing each file."""
        prefix = "OK" if success else "ERROR"
        self._append_log(f"[{prefix}] {filename}: {message}")

    def _append_log(self, text: str) -> None:
        """Appends a timestamped line to the activity log widget."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.appendPlainText(f"[{timestamp}] {text}")
        # Auto-scroll to bottom
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ------------------------------------------------------------------
    # Public API (consumed by MainWindow via lazy import)
    # ------------------------------------------------------------------

    @property
    def is_agent_running(self) -> bool:
        return bool(self._watcher and self._watcher.is_running)
