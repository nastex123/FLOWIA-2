"""Unit and integration tests for the Glassmorphism PySide6 Desktop GUI redesign."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTabWidget

from desktop.controllers.mock_backend import MOCK_DOCUMENT_ID, build_simulated_client
from desktop.ui.documents_view import DocumentsView
from desktop.ui.invoice_review_view import InvoiceReviewView
from desktop.ui.login_dialog import LoginDialog
from desktop.ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


def test_main_window_glass_and_collapsible_sidebar():
    client = build_simulated_client()
    window = MainWindow(client=client)
    
    # Check scale
    assert window.width() >= 1080
    assert window.height() >= 720
    assert window._sidebar_expanded is True
    assert window.sidebar_container.width() == 240

    # Toggle sidebar to collapsed mode
    window._toggle_sidebar()
    assert window._sidebar_expanded is False
    assert window.sidebar_container.width() == 68
    assert window.toggle_btn.text() == "▶"

    # Toggle back to expanded mode
    window._toggle_sidebar()
    assert window._sidebar_expanded is True
    assert window.sidebar_container.width() == 240
    assert window.toggle_btn.text() == "☰"


def test_documents_view_kpis_and_chip_filters():
    client = build_simulated_client()
    view = DocumentsView(client)
    view.refresh()

    # Verify KPI values are populated
    assert view.total_card._val_label.text() != "0"
    assert view.model.rowCount() == 2

    # Test chip filter for critical
    view._set_chip_filter("critical")
    assert view.model.rowCount() == 1

    # Test chip filter for all
    view._set_chip_filter("all")
    assert view.model.rowCount() == 2


def test_invoice_review_tabbed_workspace():
    client = build_simulated_client()
    review_view = InvoiceReviewView(client)
    review_view.load_document(MOCK_DOCUMENT_ID)

    # Check tab structure
    assert review_view.tabs.count() == 5
    assert review_view.tabs.tabText(0) == "📄 Resumen & Cabecera"
    assert review_view.tabs.tabText(1) == "📦 Líneas de Ítems"
    assert review_view.tabs.tabText(2) == "🛡️ Auditoría Sentinel"
    assert review_view.tabs.tabText(3) == "🧮 Validador Matemático"
    assert review_view.tabs.tabText(4) == "🔍 Evidencia & JSON"

    # Verify structured invoice data
    assert review_view.vendor_name_lbl.text() == "Suministros Industriales S.L."
    assert review_view.vendor_tax_id_lbl.text() == "B12345678"
    assert review_view.items_model.rowCount() == 2
    assert review_view.sentinel_list.count() > 0
    assert review_view.review_btn.isEnabled() is True


def test_login_dialog_elements():
    client = build_simulated_client()
    dialog = LoginDialog(client)
    assert dialog.email_edit.text() == "admin@flowmind.local"
    assert dialog.password_edit.text() == "admin123"
    assert dialog.demo_btn is not None
