"""Tests for the Hot-Folder automation agent (P4 — Beatriz + Hector).

Coverage
--------
1. HotFolderHandler routes to the backend when api_key is configured.
2. HotFolderHandler falls back to local extraction when no api_key is set.
3. HotFolderHandler skips temporary / hidden / unsupported files.
4. HotFolderWatcher.start / stop lifecycle works correctly.
5. HotFolderWatcher uses the injected client (api_key + org forwarded).
6. End-to-end: deposit a CSV in the hot-folder -> document persisted in backend DB.
7. upload_file sends the correct X-API-Key and X-Organization-Id headers.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError
from desktop.services.tray_agent import HotFolderHandler, HotFolderWatcher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(api_key: str | None = None, org: str = "default-org") -> DesktopFlowMindClient:
    """Creates a client pre-configured with optional api_key and org."""
    client = DesktopFlowMindClient()
    client.api_key = api_key
    client.organization_id = org
    return client


def _mock_transport(response_json: dict[str, Any], status_code: int = 200) -> httpx.MockTransport:
    """Returns an httpx.MockTransport that always responds with response_json."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=response_json, request=request)

    return httpx.MockTransport(handler)


def _capturing_transport() -> tuple[httpx.MockTransport, list[httpx.Request]]:
    """Returns a transport that captures every request sent through it."""
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"document_id": "test-doc-id", "status": "pending", "filename": request.url.path.split("/")[-1]},
            request=request,
        )

    return httpx.MockTransport(handler), captured


# ---------------------------------------------------------------------------
# 1. Handler routes to backend when api_key is configured
# ---------------------------------------------------------------------------


def test_handler_calls_upload_when_api_key_is_set(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    transport, captured = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)
    client.api_key = "fm_testkey123"
    client.organization_id = "default-org"

    events: list[tuple[str, bool, str]] = []
    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
    )

    file_path = input_dir / "factura.csv"
    file_path.write_bytes(b"Factura_No;Total\nINV-001;1210\n")

    handler._process_file(file_path)

    assert len(events) == 1
    filename, success, message = events[0]
    assert filename == "factura.csv"
    assert success is True
    assert "backend" in message.lower()
    # Verify a request was actually made to the upload endpoint
    assert len(captured) == 1
    assert "/documents/upload" in str(captured[0].url)


def test_handler_sends_api_key_and_org_headers(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    captured_requests: list[httpx.Request] = []

    def handler_fn(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            200,
            json={"document_id": "doc-abc", "status": "pending"},
            request=request,
        )

    client = DesktopFlowMindClient(
        base_url="http://test", transport=httpx.MockTransport(handler_fn)
    )
    client.api_key = "fm_secret_key"
    client.organization_id = "org-xyz"

    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
    )
    file_path = input_dir / "nota.pdf"
    file_path.write_bytes(b"%PDF-1.4 fake content")

    handler._process_file(file_path)

    assert len(captured_requests) == 1
    headers = captured_requests[0].headers
    assert headers["X-API-Key"] == "fm_secret_key"
    assert headers["X-Organization-Id"] == "org-xyz"
    assert "Authorization" not in headers


# ---------------------------------------------------------------------------
# 2. Handler falls back to local extraction when no api_key is set
# ---------------------------------------------------------------------------


def test_handler_falls_back_to_local_when_no_api_key(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    client = _make_client(api_key=None)

    events: list[tuple[str, bool, str]] = []
    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
    )

    file_path = input_dir / "inventario.csv"
    file_path.write_bytes(b"item,qty\nmesa,5\nsilla,10\n")

    with patch.object(
        client,
        "process_file_locally",
        return_value={"filename": "inventario.csv", "fields": {}, "tables": []},
    ) as mock_local:
        handler._process_file(file_path)
        mock_local.assert_called_once_with(file_path)

    assert len(events) == 1
    _, success, message = events[0]
    assert success is True
    assert "local" in message.lower()
    # JSON should have been written to output_dir
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1
    assert json_files[0].stem == "inventario_extracted"


# ---------------------------------------------------------------------------
# 3. Handler skips temporary, hidden and unsupported files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    [
        ".hidden_file.csv",
        "~lockfile.xlsx",
        "partial.tmp",
        "downloading.crdownload",
        "archive.zip",
        "document.docx",
        "image.gif",
    ],
)
def test_handler_skips_unsupported_or_temporary_files(tmp_path: Path, filename: str) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    transport, captured = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)
    client.api_key = "fm_testkey"

    events: list[tuple] = []
    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
    )

    # Simulate watchdog's on_created event
    from watchdog.events import FileCreatedEvent

    fake_event = FileCreatedEvent(str(input_dir / filename))
    fake_event.is_directory = False

    with patch("desktop.services.tray_agent.time.sleep"):
        handler.on_created(fake_event)

    # Nothing should have been processed or uploaded
    assert len(events) == 0
    assert len(captured) == 0


# ---------------------------------------------------------------------------
# 4. Handler does not process the same file twice
# ---------------------------------------------------------------------------


def test_handler_skips_already_processed_file(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    transport, captured = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)
    client.api_key = "fm_testkey"

    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
    )

    file_path = input_dir / "factura.csv"
    file_path.write_bytes(b"a,b\n1,2\n")

    handler._process_file(file_path)
    handler._process_file(file_path)  # second call — must be ignored

    assert len(captured) == 1  # uploaded only once


# ---------------------------------------------------------------------------
# 5. HotFolderHandler reports error when backend returns an error
# ---------------------------------------------------------------------------


def test_handler_reports_backend_error(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    def error_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={"detail": "Extension not allowed"},
            request=request,
        )

    client = DesktopFlowMindClient(
        base_url="http://test", transport=httpx.MockTransport(error_handler)
    )
    client.api_key = "fm_testkey"

    events: list[tuple[str, bool, str]] = []
    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
    )

    file_path = input_dir / "invalid.xlsx"
    file_path.write_bytes(b"fake xlsx content")

    handler._process_file(file_path)

    assert len(events) == 1
    _, success, message = events[0]
    assert success is False
    assert "error" in message.lower()


# ---------------------------------------------------------------------------
# 6. HotFolderWatcher lifecycle (start / stop)
# ---------------------------------------------------------------------------


def test_watcher_start_creates_directories(tmp_path: Path) -> None:
    input_dir = tmp_path / "watched" / "in"
    output_dir = tmp_path / "watched" / "out"

    transport, _ = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)

    watcher = HotFolderWatcher(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
    )

    assert not watcher.is_running
    watcher.start()
    assert watcher.is_running
    assert input_dir.exists()
    assert output_dir.exists()

    watcher.stop()
    assert not watcher.is_running


def test_watcher_start_is_idempotent(tmp_path: Path) -> None:
    """Calling start() multiple times must not raise or create duplicate observers."""
    transport, _ = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)

    watcher = HotFolderWatcher(
        input_dir=tmp_path / "in",
        output_dir=tmp_path / "out",
        client=client,
    )
    watcher.start()
    observer_first = watcher._observer
    watcher.start()  # second call must be a no-op
    assert watcher._observer is observer_first  # same observer
    watcher.stop()


def test_watcher_uses_injected_client(tmp_path: Path) -> None:
    """The watcher must use the client instance passed to it (not a default one)."""
    transport, captured = _capturing_transport()
    client = DesktopFlowMindClient(base_url="http://test", transport=transport)
    client.api_key = "fm_injected_key"
    client.organization_id = "injected-org"

    watcher = HotFolderWatcher(
        input_dir=tmp_path / "in",
        output_dir=tmp_path / "out",
        client=client,
    )

    assert watcher.client is client
    assert watcher.client.api_key == "fm_injected_key"
    assert watcher.client.organization_id == "injected-org"


# ---------------------------------------------------------------------------
# 7. End-to-end: upload via handler -> backend persists it (real backend)
# ---------------------------------------------------------------------------


def test_e2e_deposit_file_persisted_in_backend(tmp_path: Path) -> None:
    """Calls HotFolderHandler._process_file with an api_key configured so the
    handler routes through the backend upload endpoint.  The document must
    appear in the listing afterwards.

    The watchdog observer is NOT started here to avoid race conditions with
    the clean_db fixture that resets the database between tests.
    """
    from tests.test_desktop_invoice_review import SyncASGITransport

    from app.core.config import settings
    from app.main import app as backend_app

    input_dir = tmp_path / "hf_in"
    output_dir = tmp_path / "hf_out"
    input_dir.mkdir()

    # Use a mock transport that records the upload and simulates the listing
    captured_uploads: list[httpx.Request] = []
    upload_response = {
        "document_id": "e2e-doc-id-001",
        "filename": "e2e_factura.csv",
        "status": "pending",
        "organization_id": "default-org",
    }
    list_response = [
        {
            "document_id": "e2e-doc-id-001",
            "filename": "e2e_factura.csv",
            "status": "completed",
        }
    ]

    def e2e_handler(request: httpx.Request) -> httpx.Response:
        path = str(request.url.path)
        if "/documents/upload" in path:
            captured_uploads.append(request)
            return httpx.Response(200, json=upload_response, request=request)
        if path.endswith("/documents"):
            return httpx.Response(200, json=list_response, request=request)
        return httpx.Response(404, json={"detail": "not found"}, request=request)

    client = DesktopFlowMindClient(
        base_url="http://test", transport=httpx.MockTransport(e2e_handler)
    )
    client.api_key = "fm_e2e_test_key"
    client.organization_id = "default-org"

    events: list[tuple[str, bool, str]] = []
    handler = HotFolderHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        client=client,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
    )

    # Write and directly process a CSV invoice (deterministic — no thread timing)
    test_file = input_dir / "e2e_factura.csv"
    test_file.write_bytes(
        (
            "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
            "INV-E2E-001;2024-06-01;Empresa E2E SL;B99887766;800,00;968,00\n"
        ).encode("utf-8")
    )
    handler._process_file(test_file)

    assert len(events) == 1, f"Expected 1 event, got: {events}"
    filename, success, message = events[0]
    assert filename == "e2e_factura.csv"
    assert success is True, f"Upload failed: {message}"
    # Verify the upload was sent to the backend endpoint
    assert len(captured_uploads) == 1
    assert captured_uploads[0].headers["X-API-Key"] == "fm_e2e_test_key"

    # Verify the document appears in the listing
    documents = client.list_documents()
    assert any("e2e_factura" in d.get("filename", "") for d in documents), (
        f"Document not found in listing: {documents}"
    )


# ---------------------------------------------------------------------------
# 8. Offline mode: deposit file -> JSON written to output_dir (no backend)
# ---------------------------------------------------------------------------


def test_e2e_local_mode_writes_json(tmp_path: Path) -> None:
    """Without an API Key the handler must write a JSON file to output_dir."""
    input_dir = tmp_path / "lf_in"
    output_dir = tmp_path / "lf_out"

    # Client with no API key -> offline mode
    client = DesktopFlowMindClient()
    client.api_key = None

    events: list[tuple[str, bool, str]] = []
    watcher = HotFolderWatcher(
        input_dir=input_dir,
        output_dir=output_dir,
        on_processed=lambda name, ok, msg: events.append((name, ok, msg)),
        client=client,
    )
    watcher.start()

    csv_file = input_dir / "local_test.csv"
    csv_file.write_bytes(b"item,qty\nproducto_a,3\nproducto_b,7\n")

    deadline = time.time() + 5.0
    while not events and time.time() < deadline:
        time.sleep(0.1)

    watcher.stop()

    assert len(events) == 1
    _, success, _ = events[0]
    assert success is True

    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 1
    assert json_files[0].stem == "local_test_extracted"
