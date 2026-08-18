"""Desktop API client communicating with local FlowMind backend or direct Python engine fallback."""

from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.extractors.vision_extractor import VisionExtractor


class FlowMindApiError(RuntimeError):
    """Raised when the FlowMind backend returns an error response."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


class DesktopFlowMindClient:
    """Client for processing documents locally or via the REST API.

    The transport is injectable so tests and the demo mode can use a simulated
    backend that matches the TDD contract until P2 (invoice review API) is merged.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        transport: Optional[httpx.BaseTransport] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._transport = transport
        self.token: Optional[str] = None
        self.api_key: Optional[str] = None
        self.organization_id: Optional[str] = None
        self.default_organization_id: Optional[str] = None
        self.organizations: list[Dict[str, Any]] = []
        self.current_user: Optional[Dict[str, Any]] = None

        self.tabular_extractor = TabularExtractor()
        self.pdf_extractor = PDFExtractor()
        self.vision_extractor = VisionExtractor()

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _client(self) -> httpx.Client:
        kwargs: Dict[str, Any] = {"timeout": 30.0}
        if self._transport is not None:
            kwargs["transport"] = self._transport
        return httpx.Client(**kwargs)

    def _send_request(self, method: str, url: str, **kwargs) -> Any:
        try:
            with self._client() as client:
                response = client.request(method, url, **kwargs)
                return self._handle(response)
        except httpx.RequestError as exc:
            raise FlowMindApiError(
                503,
                f"No se pudo conectar con el servidor backend en {self.base_url}.\n"
                f"Verifica que el backend esté iniciado o ejecuta con '--demo' para modo offline.\n"
                f"Detalle: {exc}",
            ) from exc

    @staticmethod
    def _handle(response: httpx.Response) -> Any:
        if response.status_code < 400:
            return response.json()
        try:
            detail = response.json()["detail"]
        except (ValueError, KeyError):
            detail = response.text
        raise FlowMindApiError(response.status_code, str(detail))

    def _bearer_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.organization_id:
            headers["X-Organization-Id"] = self.organization_id
        return headers

    def _upload_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.organization_id:
            headers["X-Organization-Id"] = self.organization_id
        return headers

    # ------------------------------------------------------------------
    # Authentication & organization
    # ------------------------------------------------------------------

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticates with email/password and stores the JWT token."""
        data = self._send_request(
            "POST",
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.token = data.get("access_token")
        self.current_user = data.get("user")
        return data

    def me(self) -> Dict[str, Any]:
        """Fetches the authenticated user and their organizations (JWT only)."""
        data = self._send_request(
            "GET",
            f"{self.base_url}/api/v1/auth/me",
            headers=self._bearer_headers(),
        )
        self.current_user = data.get("user")
        self.organizations = data.get("organizations", [])
        default_org = data.get("default_organization") or {}
        self.default_organization_id = default_org.get("id")
        if not self.organization_id and self.default_organization_id:
            self.organization_id = self.default_organization_id
        return data

    def set_organization(self, organization_id: str) -> None:
        self.organization_id = organization_id

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def list_documents(self) -> list[Dict[str, Any]]:
        return self._send_request(
            "GET",
            f"{self.base_url}/api/v1/documents",
            headers=self._bearer_headers(),
        )

    def get_document(self, document_id: str) -> Dict[str, Any]:
        return self._send_request(
            "GET",
            f"{self.base_url}/api/v1/documents/{document_id}",
            headers=self._bearer_headers(),
        )

    def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """Uploads a file to /documents/upload using an API key (or JWT fallback)."""
        with open(file_path, "rb") as f:
            return self._send_request(
                "POST",
                f"{self.base_url}/api/v1/documents/upload",
                files={"file": (file_path.name, f, "application/octet-stream")},
                headers=self._upload_headers(),
            )

    def list_checks(self, **filters) -> Dict[str, Any]:
        """Lists findings for the tenant, optionally filtered by severity/status/document."""
        params = {k: v for k, v in filters.items() if v is not None}
        return self._send_request(
            "GET",
            f"{self.base_url}/api/v1/decision/checks",
            params=params,
            headers=self._bearer_headers(),
        )

    def review_document(self, document_id: str, note: str = "") -> Dict[str, Any]:
        """Marks a document as reviewed (financial team action)."""
        return self._send_request(
            "POST",
            f"{self.base_url}/api/v1/documents/{document_id}/review",
            json={"note": note},
            headers=self._bearer_headers(),
        )

    # ------------------------------------------------------------------
    # Local processing (offline / air-gapped mode)
    # ------------------------------------------------------------------

    def process_file_locally(self, file_path: Path) -> Dict[str, Any]:
        """Extracts structured data directly using the local engine (zero latency / air-gapped)."""
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
        """Deprecated alias of upload_file kept for the hot-folder agent (P4)."""
        if token:
            self.token = token
        try:
            return self.upload_file(file_path)
        except FlowMindApiError:
            return None