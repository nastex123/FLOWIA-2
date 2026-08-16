"""Local disk storage service with multi-tenant directory partitioning."""

import os
from pathlib import Path
from typing import BinaryIO, Union

from app.core.config import settings
from app.core.exceptions import FlowMindException


class LocalStorageService:
    """Manages document files on the local file system partitioned by tenant."""

    def __init__(self, base_path: Union[str, Path, None] = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        content: Union[bytes, BinaryIO],
        organization_id: str,
        document_id: str,
        filename: str,
    ) -> Path:
        """Saves file content into isolated tenant directory structure."""
        # Sanitize filename
        safe_filename = Path(filename).name
        tenant_dir = (self.base_path / organization_id / document_id).resolve()

        # Prevent directory traversal
        if not str(tenant_dir).startswith(str(self.base_path)):
            raise FlowMindException("Path traversal attempt detected in storage path.")

        tenant_dir.mkdir(parents=True, exist_ok=True)
        target_path = tenant_dir / safe_filename

        if isinstance(content, bytes):
            with open(target_path, "wb") as f:
                f.write(content)
        else:
            with open(target_path, "wb") as f:
                f.write(content.read())

        return target_path

    def get_file_path(
        self, organization_id: str, document_id: str, filename: str
    ) -> Path:
        """Resolves full local path ensuring tenant isolation."""
        safe_filename = Path(filename).name
        target_path = (self.base_path / organization_id / document_id / safe_filename).resolve()
        if not str(target_path).startswith(str(self.base_path)):
            raise FlowMindException("Path traversal attempt detected.")
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {target_path}")
        return target_path

    def read_bytes(
        self, organization_id: str, document_id: str, filename: str
    ) -> bytes:
        """Reads file bytes from local storage."""
        path = self.get_file_path(organization_id, document_id, filename)
        with open(path, "rb") as f:
            return f.read()
