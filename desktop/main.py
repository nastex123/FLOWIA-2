"""Entry point for the FlowMind AI PySide6 Desktop Application."""

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project backend is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication

from desktop.controllers.api_client import DesktopFlowMindClient
from desktop.ui.main_window import MainWindow


def _build_client() -> Optional[DesktopFlowMindClient]:
    if "--demo" in sys.argv:
        from desktop.controllers.mock_backend import build_simulated_client

        return build_simulated_client()

    api_url = os.environ.get("FLOWMIND_API_URL", "http://127.0.0.1:8000")
    for i, arg in enumerate(sys.argv):
        if arg == "--api-url" and i + 1 < len(sys.argv):
            api_url = sys.argv[i + 1]
        elif arg.startswith("--api-url="):
            api_url = arg.split("=", 1)[1]

    return DesktopFlowMindClient(base_url=api_url)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FlowMind AI Desktop")
    app.setOrganizationName("FlowMind")

    window = MainWindow(client=_build_client())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()