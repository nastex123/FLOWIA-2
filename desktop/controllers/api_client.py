"""Desktop API client communicating with local FlowMind backend or direct Python engine fallback."""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import httpx

from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.extractors.vision_extractor import VisionExtractor


class DesktopFlowMindClient:
    """Client for processing documents locally or via REST API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.tabular_extractor = TabularExtractor()
        self.pdf_extractor = PDFExtractor()
        self.vision_extractor = VisionExtractor()

    def process_file_locally(self, file_path: Path) -> Dict[str, Any]:
        """Extracts structured data directly using local engine (zero latency / air-gapped)."""
        ext = file_path.suffix.lower().lstrip(".")
        filename = file_path.name

        if ext in ("xlsx", "xls", "csv"):
            res = self.tabular_extractor.extract(file_input=file_path, filename=filename)
        elif ext == "pdf":
            res = self.pdf_extractor.extract(file_input=file_path, filename=filename)
        elif ext in ("png", "jpg", "jpeg", "tiff", "bmp", "webp"):
            res = self.vision_extractor.extract(file_input=file_path, filename=filename)
        else:
            raise ValueError(f"Formato no compatible: .{ext}")

        return res.model_dump()

    def send_to_backend(self, file_path: Path, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Sends document to FastAPI backend via REST API."""
        try:
            url = f"{self.base_url}/api/v1/extract"
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, files=files, headers=headers)
                    if response.status_code == 200:
                        return response.json()
        except Exception:
            pass
        return None
