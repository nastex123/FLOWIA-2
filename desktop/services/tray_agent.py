"""Hot-Folder filesystem watcher and System Tray background agent."""

import os
import json
import time
from pathlib import Path
from typing import Callable, Optional
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

from desktop.controllers.api_client import DesktopFlowMindClient


class HotFolderHandler(FileSystemEventHandler):
    """Event handler that detects new documents dropped into the hot-folder."""

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        client: DesktopFlowMindClient,
        on_processed: Optional[Callable[[str, bool, str], None]] = None,
    ):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.client = client
        self.on_processed = on_processed
        self.processed_files = set()

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        # Avoid processing partial temporary downloads
        if file_path.name.startswith((".", "~")) or file_path.suffix.lower() in (".tmp", ".crdownload"):
            return

        # Give the operating system a moment to finish writing file
        time.sleep(0.5)
        self._process_file(file_path)

    def _process_file(self, file_path: Path) -> None:
        if file_path.name in self.processed_files or not file_path.exists():
            return
        self.processed_files.add(file_path.name)

        try:
            # 1. Process document
            result = self.client.process_file_locally(file_path)

            # 2. Save structured JSON to output folder
            self.output_dir.mkdir(parents=True, exist_ok=True)
            out_file = self.output_dir / f"{file_path.stem}_extracted.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            if self.on_processed:
                self.on_processed(file_path.name, True, f"Procesado guardado en {out_file.name}")

        except Exception as e:
            if self.on_processed:
                self.on_processed(file_path.name, False, f"Error: {str(e)}")


class HotFolderWatcher:
    """Manages the background watchdog observer thread."""

    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        on_processed: Optional[Callable[[str, bool, str], None]] = None,
    ):
        base_path = Path.cwd() / "hot_folder"
        self.input_dir = input_dir or (base_path / "in")
        self.output_dir = output_dir or (base_path / "out")
        self.on_processed = on_processed
        self.client = DesktopFlowMindClient()
        self.observer: Optional[Observer] = None
        self.is_running = False

    def start(self) -> None:
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

        self.observer = Observer()
        self.observer.schedule(handler, str(self.input_dir), recursive=False)
        self.observer.start()
        self.is_running = True

    def stop(self) -> None:
        if self.observer and self.is_running:
            self.observer.stop()
            self.observer.join(timeout=2.0)
            self.is_running = False
