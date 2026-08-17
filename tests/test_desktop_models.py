"""Unit tests for the Desktop Virtual Table Model and Hot-Folder Agent."""

import json
from pathlib import Path
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QApplication

from desktop.models.table_model import VirtualDataTableModel
from desktop.services.tray_agent import HotFolderHandler, HotFolderWatcher
from desktop.controllers.api_client import DesktopFlowMindClient

# Ensure a QCoreApplication exists for Qt Model testing
app = QApplication.instance() or QApplication([])


def test_virtual_data_table_model_basic():
    headers = ["SKU", "Description", "Price"]
    records = [
        {"SKU": "A001", "Description": "Laptop Stand", "Price": 29.99},
        {"SKU": "A002", "Description": "Mechanical Keyboard", "Price": 89.50},
    ]

    model = VirtualDataTableModel(headers=headers, records=records)

    assert model.rowCount() == 2
    assert model.columnCount() == 3

    # Test data retrieval
    idx_sku = model.index(0, 0)
    assert model.data(idx_sku, Qt.ItemDataRole.DisplayRole) == "A001"

    idx_desc = model.index(1, 1)
    assert model.data(idx_desc, Qt.ItemDataRole.DisplayRole) == "Mechanical Keyboard"

    # Test headers
    assert model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "SKU"
    assert model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Description"


def test_hot_folder_watcher_lifecycle(tmp_path):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"

    watcher = HotFolderWatcher(input_dir=in_dir, output_dir=out_dir)
    assert watcher.is_running is False

    watcher.start()
    assert watcher.is_running is True
    assert in_dir.exists()
    assert out_dir.exists()

    watcher.stop()
    assert watcher.is_running is False
