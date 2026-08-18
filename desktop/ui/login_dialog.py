"""Gothic Authentication Chamber Dialog for FlowMind AI Desktop."""

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
    """Gothic Authentication Chamber for FlowMind AI Desktop."""

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("Autenticacion — FlowMind AI")
        self.setMinimumWidth(580)
        self.setMinimumHeight(490)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 28, 28, 28)

        # Header Logo & Subtitle
        header_frame = QFrame()
        header_frame.setObjectName("glassCard")
        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(18, 16, 18, 16)

        header_label = QLabel("<h2 style='margin: 0; color: #fda4af; font-family: Georgia, serif; font-size: 22px; letter-spacing: 1px;'>FLOWMIND AI</h2><p style='margin: 4px 0 0 0; color: #a8a29e; font-size: 13px;'>Catedral de Inteligencia Financiera & Auditoria Local</p>")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(header_label)
        layout.addWidget(header_frame)

        # Main Tabs
        tabs = QTabWidget()
        tabs.setObjectName("glassTabs")

        # TAB 1: JWT Login & Demo
        jwt_tab = QWidget()
        jwt_form = QFormLayout(jwt_tab)
        jwt_form.setSpacing(14)
        jwt_form.setContentsMargins(14, 18, 14, 18)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("admin@flowmind.local")
        self.email_edit.setText("admin@flowmind.local")
        self.email_edit.setMinimumHeight(38)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("admin123")
        self.password_edit.setText("admin123")
        self.password_edit.setMinimumHeight(38)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.login_btn = QPushButton("Conectar al Servidor")
        self.login_btn.setMinimumHeight(42)
        self.login_btn.clicked.connect(self._on_login)

        self.demo_btn = QPushButton("Modo Cripta Offline")
        self.demo_btn.setObjectName("successButton")
        self.demo_btn.setMinimumHeight(42)
        self.demo_btn.clicked.connect(self._on_demo_mode)

        btn_row.addWidget(self.login_btn, stretch=1)
        btn_row.addWidget(self.demo_btn, stretch=1)

        self.org_combo = QComboBox()
        self.org_combo.setMinimumHeight(38)
        self.org_combo.setEnabled(False)

        jwt_form.addRow("<span style='color: #fda4af; font-family: Georgia, serif; font-weight: 600;'>Usuario / Email:</span>", self.email_edit)
        jwt_form.addRow("<span style='color: #fda4af; font-family: Georgia, serif; font-weight: 600;'>Contrasena:</span>", self.password_edit)
        jwt_form.addRow("", btn_row)
        jwt_form.addRow("<span style='color: #fda4af; font-family: Georgia, serif; font-weight: 600;'>Santuario / Org:</span>", self.org_combo)
        tabs.addTab(jwt_tab, "Usuario (JWT / Cripta)")

        # TAB 2: API Key Mode
        api_tab = QWidget()
        api_form = QFormLayout(api_tab)
        api_form.setSpacing(14)
        api_form.setContentsMargins(14, 18, 14, 18)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("fm_...")
        self.api_key_edit.setMinimumHeight(38)

        self.api_org_edit = QLineEdit()
        self.api_org_edit.setPlaceholderText("default-org (opcional)")
        self.api_org_edit.setMinimumHeight(38)

        api_form.addRow("<span style='color: #fda4af; font-family: Georgia, serif; font-weight: 600;'>API Key:</span>", self.api_key_edit)
        api_form.addRow("<span style='color: #fda4af; font-family: Georgia, serif; font-weight: 600;'>Organizacion:</span>", self.api_org_edit)
        tabs.addTab(api_tab, "Clave API")

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
            QMessageBox.critical(self, "Error de autenticacion", e.detail)
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
                    "Santuario no disponible",
                    f"{e.detail}\n\n¿Deseas ingresar en 'Modo Cripta Offline' para explorar la catedral local?",
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
                "Configuracion incompleta",
                "Inicia sesion con usuario, activa el Modo Cripta o introduce una API Key.",
            )