"""Entry point for the FlowMind AI PySide6 Desktop Application."""

import sys
from pathlib import Path

# Ensure project backend is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication
from desktop.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FlowMind AI Desktop")
    app.setOrganizationName("FlowMind")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
