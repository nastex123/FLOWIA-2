"""Login dialog for the FlowMind desktop financial app (JWT + API Key modes)."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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
    """Authenticates against the backend with JWT, API key, or Demo Mode."""

    def __init__(self, client: DesktopFlowMindClient, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("Iniciar sesión — FlowMind AI")
        self.setMinimumWidth(440)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("<h2>🧠 FlowMind AI</h2><p style='color: #94a3b8;'>Plataforma de Gestión Financiera & Auditoría Local</p>")
        layout.addWidget(header_label)

        tabs = QTabWidget()

        jwt_tab = QWidget()
        jwt_form = QFormLayout(jwt_tab)
        jwt_form.setSpacing(10)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("admin@flowmind.local")
        self.email_edit.setText("admin@flowmind.local")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("admin123")
        self.password_edit.setText("admin123")
        
        btn_row = QHBoxLayout()
        self.login_btn = QPushButton("Conectar & Cargar")
        self.login_btn.clicked.connect(self._on_login)
        self.demo_btn = QPushButton("Modo Demo Offline")
        self.demo_btn.setStyleSheet("background-color: #059669; color: white;")
        self.demo_btn.clicked.connect(self._on_demo_mode)
        btn_row.addWidget(self.login_btn)
        btn_row.addWidget(self.demo_btn)

        self.org_combo = QComboBox()
        self.org_combo.setEnabled(False)

        jwt_form.addRow("Correo:", self.email_edit)
        jwt_form.addRow("Contraseña:", self.password_edit)
        jwt_form.addRow("", btn_row)
        jwt_form.addRow("Organización:", self.org_combo)
        tabs.addTab(jwt_tab, "Usuario (JWT / Demo)")

        api_tab = QWidget()
        api_form = QFormLayout(api_tab)
        api_form.setSpacing(10)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("fm_...")
        self.api_org_edit = QLineEdit()
        self.api_org_edit.setPlaceholderText("default-org (opcional)")
        api_form.addRow("API Key:", self.api_key_edit)
        api_form.addRow("Organización:", self.api_org_edit)
        tabs.addTab(api_tab, "API Key")

        layout.addWidget(tabs)

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
                # Si falló la conexión directa y hay opción demo
                reply = QMessageBox.question(
                    self,
                    "Backend no disponible",
                    f"{e.detail}\n\n¿Deseas continuar en 'Modo Demo' para explorar la interfaz?",
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