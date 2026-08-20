"""Hot-Folder filesystem watcher and System Tray background agent.

Flow when an API Key is configured:
    new file detected
        --> DesktopFlowMindClient.upload_file(path)
            --> POST /api/v1/documents/upload  (X-API-Key + X-Organization-Id)
                --> backend: persist, validate, trigger rules/webhooks
        --> QSystemTrayIcon.showMessage() with result

Offline fallback (no API Key):
    new file detected
        --> DesktopFlowMindClient.process_file_locally(path)
            --> structured JSON written to output_dir
"""

import json
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from desktop.controllers.api_client import DesktopFlowMindClient, FlowMindApiError

# Extensions accepted for processing
_ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
# Prefixes / suffixes that indicate an incomplete or temporary file
_SKIP_PREFIXES = (".", "~")
_SKIP_SUFFIXES = (".tmp", ".crdownload", ".part")


class HotFolderHandler(FileSystemEventHandler):
    """Event handler that detects new documents dropped into the hot-folder.

    When the shared ``DesktopFlowMindClient`` has an ``api_key`` set, each
    incoming file is uploaded to the FlowMind backend so it is persisted,
    validated and fed into the automation rules pipeline.

    When no ``api_key`` is configured the file is processed offline using the
    local extraction engines and the result is written to ``output_dir``.
    """

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        client: DesktopFlowMindClient,
        on_processed: Optional[Callable[[str, bool, str], None]] = None,
    ) -> None:
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.client = client
        self.on_processed = on_processed
        self.processed_files: set[str] = set()

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip hidden / partial downloads
        if (
            file_path.name.startswith(_SKIP_PREFIXES)
            or file_path.suffix.lower() in _SKIP_SUFFIXES
        ):
            return

        # Only handle known document extensions
        if file_path.suffix.lower() not in _ALLOWED_EXTENSIONS:
            return

        # Give the OS a moment to finish writing the file to disk
        time.sleep(0.5)
        self._process_file(file_path)

    def _process_file(self, file_path: Path) -> None:
        """Processes a single file either via the backend API or locally."""
        if file_path.name in self.processed_files or not file_path.exists():
            return
        self.processed_files.add(file_path.name)

        if self.client.api_key:
            self._process_via_backend(file_path)
        else:
            self._process_locally(file_path)

    def _process_via_backend(self, file_path: Path) -> None:
        """Uploads the file to the FlowMind backend using the configured API Key.

        The backend pipeline will persist the document, run the invoice
        structurizer, mathematical validator, Sentinel and trigger any
        configured automation rules/webhooks.
        """
        try:
            result = self.client.upload_file(file_path)
            document_id = result.get("document_id", "")
            status = result.get("status", "queued")
            message = (
                f"Enviado al backend — documento {document_id[:8]}... ({status})"
            )
            if self.on_processed:
                self.on_processed(file_path.name, True, message)
        except FlowMindApiError as exc:
            error_msg = f"Error al enviar al backend [{exc.status_code}]: {exc.detail}"
            if self.on_processed:
                self.on_processed(file_path.name, False, error_msg)
        except Exception as exc:  # noqa: BLE001
            if self.on_processed:
                self.on_processed(file_path.name, False, f"Error inesperado: {exc}")

    def _process_locally(self, file_path: Path) -> None:
        """Offline fallback: extracts locally and writes JSON to output_dir."""
        try:
            result = self.client.process_file_locally(file_path)

            self.output_dir.mkdir(parents=True, exist_ok=True)
            out_file = self.output_dir / f"{file_path.stem}_extracted.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            if self.on_processed:
                self.on_processed(
                    file_path.name,
                    True,
                    f"Procesado localmente — guardado en {out_file.name}",
                )
        except Exception as exc:  # noqa: BLE001
            if self.on_processed:
                self.on_processed(file_path.name, False, f"Error en extraccion local: {exc}")


class HotFolderWatcher:
    """Manages the background watchdog observer thread.

    Usage
    -----
    - When ``client.api_key`` is set the handler sends each new file to the
      FlowMind backend (``POST /api/v1/documents/upload``).
    - Without an API Key it falls back to local extraction, writing structured
      JSON files to ``output_dir``.

    Parameters
    ----------
    input_dir:
        Directory to watch for new files.  Defaults to ``./hot_folder/in``.
    output_dir:
        Directory where offline JSON results are written.
        Defaults to ``./hot_folder/out``.
    on_processed:
        Optional callback ``(filename, success, message) -> None`` called after
        each file is handled.  The callback runs on the watchdog thread; use
        Qt's signal/slot mechanism if you need to update the UI safely.
    client:
        Shared ``DesktopFlowMindClient`` instance.  If not provided a new
        default client is created.  Inject a pre-configured client (with API
        Key / org set) from ``SettingsView`` before calling ``start()``.
    """

    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        on_processed: Optional[Callable[[str, bool, str], None]] = None,
        client: Optional[DesktopFlowMindClient] = None,
    ) -> None:
        base_path = Path.cwd() / "hot_folder"
        self.input_dir: Path = input_dir or (base_path / "in")
        self.output_dir: Path = output_dir or (base_path / "out")
        self.on_processed = on_processed
        self.client: DesktopFlowMindClient = client or DesktopFlowMindClient()
        self._observer: Optional[Observer] = None
        self.is_running: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Starts the filesystem observer in a background thread."""
        if self.is_running:
            return

        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        handler = HotFolderHandler(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            client=self.client,
            on_processed=self.on_processed,
        )

        self._observer = Observer()
        self._observer.schedule(handler, str(self.input_dir), recursive=False)
        self._observer.start()
        self.is_running = True

    def stop(self) -> None:
        """Stops the filesystem observer and waits for clean shutdown."""
        if self._observer and self.is_running:
            self._observer.stop()
            self._observer.join(timeout=2.0)
            self._observer = None
            self.is_running = False
