"""Modern Dark Design System and Stylesheet for FlowMind AI Desktop."""

DARK_THEME_QSS = """
/* Global Window & Fonts */
QMainWindow {
    background-color: #0b0f17;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

QWidget {
    color: #f1f5f9;
    font-size: 13px;
}

/* Toolbar */
QToolBar {
    background-color: #111827;
    border-bottom: 1px solid #1f2937;
    padding: 8px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: #1f2937;
    color: #f1f5f9;
    font-weight: 600;
    padding: 8px 14px;
    border-radius: 6px;
    border: 1px solid #374151;
}

QToolButton:hover {
    background-color: #374151;
    border-color: #4b5563;
}

QToolButton:pressed {
    background-color: #111827;
}

/* Push Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #374151;
    color: #9ca3af;
}

/* Sidebar List */
QListWidget#sidebar {
    background-color: #111827;
    color: #94a3b8;
    border-right: 1px solid #1f2937;
    border-top: none;
    border-bottom: none;
    border-left: none;
    padding: 12px 6px;
    outline: none;
}

QListWidget#sidebar::item {
    padding: 10px 14px;
    margin-bottom: 4px;
    border-radius: 8px;
    font-weight: 600;
    color: #94a3b8;
}

QListWidget#sidebar::item:hover {
    background-color: #1f2937;
    color: #f1f5f9;
}

QListWidget#sidebar::item:selected {
    background-color: #1e3a8a;
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
}

/* Cards & Frames */
QFrame#card {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 14px;
}

QFrame#kpiCard {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 12px;
}

/* Line Edits & Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #111827;
    color: #f1f5f9;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #0f172a;
}

/* Combo Boxes */
QComboBox {
    background-color: #111827;
    color: #f1f5f9;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
}

QComboBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #111827;
    color: #f1f5f9;
    border: 1px solid #374151;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border-radius: 6px;
    padding: 4px;
}

/* Tables */
QTableView {
    background-color: #111827;
    color: #f1f5f9;
    gridline-color: #1f2937;
    border: 1px solid #1f2937;
    border-radius: 8px;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
    outline: none;
}

QTableView::item {
    padding: 6px 10px;
}

QTableView::item:selected {
    background-color: #1e3a8a;
}

QHeaderView::section {
    background-color: #0b0f17;
    color: #94a3b8;
    font-weight: bold;
    font-size: 12px;
    border-bottom: 1px solid #1f2937;
    border-right: 1px solid #1f2937;
    border-top: none;
    border-left: none;
    padding: 8px 10px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1f2937;
    border-radius: 8px;
    background-color: #111827;
    padding: 8px;
}

QTabBar::tab {
    background-color: #1f2937;
    color: #94a3b8;
    font-weight: 600;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #111827;
    color: #60a5fa;
    border-top: 2px solid #3b82f6;
}

/* Status Bar */
QStatusBar {
    background-color: #0b0f17;
    color: #64748b;
    border-top: 1px solid #1f2937;
    font-size: 12px;
    padding: 4px 8px;
}

/* Splitter */
QSplitter::handle {
    background-color: #1f2937;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #3b82f6;
}
"""
