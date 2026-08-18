"""High-performance virtual QAbstractTableModel for PySide6 table rendering."""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

_SEVERITY_COLORS = {
    "ok": QColor("#22c55e"),
    "warning": QColor("#f59e0b"),
    "critical": QColor("#ef4444"),
    "info": QColor("#3b82f6"),
    "unknown": QColor("#94a3b8"),
}


class VirtualDataTableModel(QAbstractTableModel):
    """Virtual table model capable of rendering large datasets with smooth scrolling and zero lag."""

    def __init__(self, headers: Optional[List[str]] = None, records: Optional[List[Dict[str, Any]]] = None):
        super().__init__()
        self._headers = headers or []
        self._records = records or []
        self._severity_column: Optional[int] = None

    def set_data(self, headers: List[str], records: List[Dict[str, Any]]) -> None:
        self.beginResetModel()
        self._headers = headers
        self._records = records
        self.endResetModel()

    def set_severity_column(self, column: Optional[int]) -> None:
        """Marks a column to be colored by severity value (ok/warning/critical/info)."""
        self._severity_column = column

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._records)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if 0 <= row < len(self._records) and 0 <= col < len(self._headers):
            key = self._headers[col]
            value = self._records[row].get(key, "")

            if role == Qt.ItemDataRole.DisplayRole:
                return str(value) if value is not None else ""
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace(".", "", 1).replace(",", "", 1).isdigit()):
                    return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            elif role == Qt.ItemDataRole.ForegroundRole and col == self._severity_column:
                return _SEVERITY_COLORS.get(str(value).lower(), _SEVERITY_COLORS["unknown"])

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self._headers):
                return self._headers[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None