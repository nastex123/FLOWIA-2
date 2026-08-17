"""Native PySide6 Desktop User Interface for FlowMind AI."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
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
    QStatusBar,
    QSystemTrayIcon,
    QTableView,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient
from desktop.models.table_model import VirtualDataTableModel
from desktop.services.tray_agent import HotFolderWatcher


class MainWindow(QMainWindow):
    """FlowMind AI Desktop Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowMind AI — Native Desktop Suite (100% Local)")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.client = DesktopFlowMindClient()
        self.hot_folder_watcher = HotFolderWatcher(on_processed=self._on_hot_folder_event)
        self.table_model = VirtualDataTableModel()

        self._setup_dark_theme()
        self._init_ui()
        self._setup_tray_icon()

    def _setup_dark_theme(self) -> None:
        """Applies modern dark palette."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e293b"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1e293b"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#3b82f6"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QToolBar { background-color: #1e293b; border-bottom: 1px solid #334155; padding: 6px; }
            QToolButton { color: #f8fafc; font-weight: bold; padding: 6px 12px; border-radius: 4px; }
            QToolButton:hover { background-color: #334155; }
            QTableView { background-color: #1e293b; color: #f8fafc; gridline-color: #334155; border: 1px solid #334155; border-radius: 6px; }
            QHeaderView::section { background-color: #0f172a; color: #94a3b8; font-weight: bold; border: 1px solid #334155; padding: 4px; }
            QTextEdit, QListWidget { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 6px; padding: 8px; font-family: monospace; }
            QStatusBar { background-color: #1e293b; color: #94a3b8; font-size: 12px; }
            QLabel { color: #f8fafc; }
        """)

    def _init_ui(self) -> None:
        # 1. Toolbar
        toolbar = QToolBar("Main Actions")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        open_action = QAction("📂 Abrir Documento", self)
        open_action.triggered.connect(self._open_file_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        self.hotfolder_btn = QPushButton("▶ Activar Hot-Folder Agent")
        self.hotfolder_btn.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        self.hotfolder_btn.clicked.connect(self._toggle_hot_folder)
        toolbar.addWidget(self.hotfolder_btn)

        # 2. Main Central Splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left Panel: Fields & Details
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl_fields = QLabel("<b>Campos Clave Extraídos & Metadatos</b>")
        left_layout.addWidget(lbl_fields)

        self.fields_text = QTextEdit()
        self.fields_text.setReadOnly(True)
        self.fields_text.setPlaceholderText("Selecciona o arrastra un archivo para procesar...")
        left_layout.addWidget(self.fields_text)

        splitter.addWidget(left_widget)

        # Right Panel: Tabular Grid Viewer
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        lbl_grid = QLabel("<b>Vista de Tabla Estructurada (Reconciliation Grid)</b>")
        right_layout.addWidget(lbl_grid)

        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table_view)

        splitter.addWidget(right_widget)
        splitter.setSizes([450, 750])

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo — Modo 100% Local (Zero Cloud Data Leakage)")

    def _setup_tray_icon(self) -> None:
        """Sets up system tray notification icon."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("FlowMind AI Desktop Agent")

    def _open_file_dialog(self) -> None:
        file_filter = "Todos los compatibles (*.xlsx *.xls *.csv *.pdf *.png *.jpg *.jpeg);;Hojas de cálculo (*.xlsx *.xls *.csv);;PDFs (*.pdf);;Imágenes (*.png *.jpg *.jpeg)"
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar documento de negocio", "", file_filter)
        if path:
            self.process_file(Path(path))

    def process_file(self, file_path: Path) -> None:
        self.status_bar.showMessage(f"Procesando '{file_path.name}'...")
        try:
            res = self.client.process_file_locally(file_path)

            # Display extracted fields
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

            # Display tables
            tables = res.get("tables", [])
            if tables:
                headers = tables[0].get("headers", [])
                records = tables[0].get("records", [])
                self.table_model.set_data(headers, records)
                self.status_bar.showMessage(f"Completado en {res.get('processing_time_ms', 0)}ms — {len(records)} filas en tabla.")
            else:
                self.table_model.set_data([], [])
                self.status_bar.showMessage(f"Completado en {res.get('processing_time_ms', 0)}ms — Sin tablas tabulares.")

        except Exception as e:
            QMessageBox.critical(self, "Error de extracción", f"No se pudo procesar el archivo:\n{str(e)}")
            self.status_bar.showMessage("Error en procesamiento.")

    def _toggle_hot_folder(self) -> None:
        if not self.hot_folder_watcher.is_running:
            self.hot_folder_watcher.start()
            self.hotfolder_btn.setText("⏹ Detener Hot-Folder Agent")
            self.hotfolder_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
            self.status_bar.showMessage(f"Hot-Folder activo monitorizando: {self.hot_folder_watcher.input_dir}")
        else:
            self.hot_folder_watcher.stop()
            self.hotfolder_btn.setText("▶ Activar Hot-Folder Agent")
            self.hotfolder_btn.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
            self.status_bar.showMessage("Hot-Folder detenido.")

    def _on_hot_folder_event(self, filename: str, success: bool, message: str) -> None:
        msg_type = "Éxito" if success else "Error"
        self.status_bar.showMessage(f"[Hot-Folder] {filename}: {message}")
