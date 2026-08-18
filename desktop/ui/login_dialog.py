"""Login dialog for the FlowMind desktop financial app (Glassmorphism + Demo Mode)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError


class LoginDialog(QDialog):
    """Modern Glassmorphism Authentication Dialog for FlowMind AI Desktop."""

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("Iniciar Sesión — FlowMind AI")
        self.setMinimumWidth(480)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header Logo & Subtitle
        header_frame = QFrame()
        header_frame.setObjectName("glassCard")
        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(14, 12, 14, 12)

        header_label = QLabel("<h2 style='margin: 0; color: #38bdf8; font-size: 20px;'>🧠 FlowMind AI</h2><p style='margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;'>Suite de Gestión Financiera, Extracción & Auditoría Local</p>")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(header_label)
        layout.addWidget(header_frame)

        # Main Tabs
        tabs = QTabWidget()
        tabs.setObjectName("glassTabs")

        # TAB 1: JWT Login & Demo
        jwt_tab = QWidget()
        jwt_form = QFormLayout(jwt_tab)
        jwt_form.setSpacing(12)
        jwt_form.setContentsMargins(12, 16, 12, 16)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("admin@flowmind.local")
        self.email_edit.setText("admin@flowmind.local")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("admin123")
        self.password_edit.setText("admin123")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.login_btn = QPushButton("Conectar al Servidor")
        self.login_btn.clicked.connect(self._on_login)

        self.demo_btn = QPushButton("✨ Modo Demo Offline")
        self.demo_btn.setObjectName("successButton")
        self.demo_btn.clicked.connect(self._on_demo_mode)

        btn_row.addWidget(self.login_btn)
        btn_row.addWidget(self.demo_btn)

        self.org_combo = QComboBox()
        self.org_combo.setEnabled(False)

        jwt_form.addRow("<span style='color: #cbd5e1; font-weight: 600;'>Usuario / Email:</span>", self.email_edit)
        jwt_form.addRow("<span style='color: #cbd5e1; font-weight: 600;'>Contraseña:</span>", self.password_edit)
        jwt_form.addRow("", btn_row)
        jwt_form.addRow("<span style='color: #cbd5e1; font-weight: 600;'>Organización:</span>", self.org_combo)
        tabs.addTab(jwt_tab, "Usuario (JWT / Demo)")

        # TAB 2: API Key Mode
        api_tab = QWidget()
        api_form = QFormLayout(api_tab)
        api_form.setSpacing(12)
        api_form.setContentsMargins(12, 16, 12, 16)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("fm_...")

        self.api_org_edit = QLineEdit()
        self.api_org_edit.setPlaceholderText("default-org (opcional)")

        api_form.addRow("<span style='color: #cbd5e1; font-weight: 600;'>API Key:</span>", self.api_key_edit)
        api_form.addRow("<span style='color: #cbd5e1; font-weight: 600;'>Organización:</span>", self.api_org_edit)
        tabs.addTab(api_tab, "API Key")

        layout.addWidget(tabs)

        # Dialog Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_demo_mode(self) -> None:
        from desktop.controllers.mock_backend import build_simulated_client, MOCK_ORGANIZATIONS

        simulated = build_simulated_client()
        self.client._transport = simulated._transport
        self.client.token = "mock-jwt-token"
        self.client.organization_id = "default-org"
        self.client.organizations = MOCK_ORGANIZATIONS
        self.accept()

    def _on_login(self) -> None:
        try:
            self.client.login(self.email_edit.text().strip(), self.password_edit.text())
            self.client.me()
        except FlowMindApiError as e:
            QMessageBox.critical(self, "Error de autenticación", e.detail)
            return

        self.org_combo.clear()
        for org in self.client.organizations:
            self.org_combo.addItem(org.get("name", org.get("id", "")), org.get("id"))
        if self.client.default_organization_id:
            index = self.org_combo.findData(self.client.default_organization_id)
            if index >= 0:
                self.org_combo.setCurrentIndex(index)
        self.org_combo.setEnabled(True)

    def _on_accept(self) -> None:
        if self.org_combo.isEnabled():
            org_id = self.org_combo.currentData()
            if org_id:
                self.client.set_organization(org_id)
            self.accept()
            return

        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        if email and password:
            try:
                self.client.login(email, password)
                self.client.me()
                if self.client.default_organization_id:
                    self.client.set_organization(self.client.default_organization_id)
                self.accept()
                return
            except FlowMindApiError as e:
                reply = QMessageBox.question(
                    self,
                    "Backend no disponible",
                    f"{e.detail}\n\n¿Deseas continuar en 'Modo Demo Offline' para explorar la interfaz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._on_demo_mode()
                return

        api_key = self.api_key_edit.text().strip()
        if api_key:
            self.client.api_key = api_key
            org_id = self.api_org_edit.text().strip()
            if org_id:
                self.client.set_organization(org_id)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Configuración incompleta",
                "Inicia sesión con usuario, activa el Modo Demo o introduce una API Key.",
            )