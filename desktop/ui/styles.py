"""Glassmorphism Cyber-Dark Design System and Stylesheet for FlowMind AI Desktop."""

DARK_THEME_QSS = """
/* ============================================================================
   1. GLOBAL WINDOW, DIALOGS & TYPOGRAPHY HIERARCHY
   ============================================================================ */
QMainWindow {
    background-color: #070a12;
    color: #f8fafc;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, sans-serif;
}

QDialog {
    background-color: #090e1a;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 12px;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QWidget {
    color: #f1f5f9;
    font-size: 14px;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

/* ============================================================================
   2. GLASSMORPHISM CARDS & CONTAINERS
   ============================================================================ */
QFrame#glassCard, QFrame#card {
    background-color: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 16px;
}

QFrame#glassCard:hover, QFrame#card:hover {
    border: 1px solid rgba(56, 189, 248, 0.45);
    background-color: rgba(15, 23, 42, 0.85);
}

QFrame#kpiCard {
    background-color: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(59, 130, 246, 0.22);
    border-radius: 12px;
    padding: 16px 18px;
}

QFrame#kpiCard:hover {
    background-color: rgba(30, 41, 59, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.65);
}

QFrame#glassPanel {
    background-color: rgba(11, 17, 32, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 12px;
    padding: 18px;
}

QFrame#actionBar {
    background-color: rgba(15, 23, 42, 0.92);
    border-top: 1px solid rgba(56, 189, 248, 0.25);
    padding: 12px 20px;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}

/* ============================================================================
   3. SIDEBAR NAVIGATION & COLLAPSE CONTROLS
   ============================================================================ */
QWidget#sidebarContainer {
    background-color: rgba(10, 15, 29, 0.95);
    border-right: 1px solid rgba(148, 163, 184, 0.14);
}

QListWidget#sidebar {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    padding: 12px 8px;
    outline: none;
}

QListWidget#sidebar::item {
    padding: 12px 16px;
    margin-bottom: 6px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    color: #94a3b8;
}

QListWidget#sidebar::item:hover {
    background-color: rgba(30, 41, 59, 0.70);
    color: #f8fafc;
    border-left: 2px solid rgba(56, 189, 248, 0.60);
}

QListWidget#sidebar::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(30, 58, 138, 0.85), stop:1 rgba(14, 165, 233, 0.35));
    color: #38bdf8;
    font-weight: 700;
    border-left: 4px solid #38bdf8;
}

QPushButton#sidebarToggle {
    background-color: rgba(30, 41, 59, 0.60);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 8px;
    font-size: 15px;
    font-weight: bold;
    padding: 6px 10px;
    min-width: 36px;
    min-height: 36px;
}

QPushButton#sidebarToggle:hover {
    background-color: rgba(56, 189, 248, 0.20);
    color: #38bdf8;
    border-color: rgba(56, 189, 248, 0.50);
}

/* ============================================================================
   4. BUTTONS & INTERACTIVE CONTROLS
   ============================================================================ */
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #0284c7);
    color: #ffffff;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid rgba(56, 189, 248, 0.30);
    min-height: 22px;
}

QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #0369a1);
    border-color: rgba(56, 189, 248, 0.75);
}

QPushButton:pressed {
    background-color: #1e3a8a;
}

QPushButton:disabled {
    background-color: rgba(30, 41, 59, 0.50);
    color: #64748b;
    border-color: rgba(148, 163, 184, 0.10);
}

QPushButton#secondaryButton {
    background-color: rgba(30, 41, 59, 0.70);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.20);
}

QPushButton#secondaryButton:hover {
    background-color: rgba(51, 65, 85, 0.85);
    color: #ffffff;
    border-color: rgba(148, 163, 184, 0.40);
}

QPushButton#successButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #0d9488);
    color: #ffffff;
    border: 1px solid rgba(52, 211, 153, 0.40);
    font-size: 14px;
    font-weight: 700;
    padding: 11px 22px;
}

QPushButton#successButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #0f766e);
    border-color: rgba(52, 211, 153, 0.80);
}

/* Chip Filter Buttons */
QPushButton#chipFilter {
    background-color: rgba(30, 41, 59, 0.60);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton#chipFilter:hover {
    background-color: rgba(51, 65, 85, 0.80);
    color: #f1f5f9;
    border-color: rgba(56, 189, 248, 0.40);
}

QPushButton#chipFilter[active="true"] {
    background-color: rgba(14, 165, 233, 0.20);
    color: #38bdf8;
    border: 1px solid #38bdf8;
}

/* ============================================================================
   5. INPUTS, TEXT FIELDS & COMBOBOXES
   ============================================================================ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: rgba(15, 23, 42, 0.85);
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #38bdf8;
    background-color: rgba(15, 23, 42, 0.95);
}

QComboBox {
    background-color: rgba(15, 23, 42, 0.85);
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 8px;
    padding: 9px 14px;
    min-height: 24px;
    font-size: 14px;
}

QComboBox:focus {
    border: 1px solid #38bdf8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid rgba(56, 189, 248, 0.30);
    selection-background-color: #1e3a8a;
    selection-color: #38bdf8;
    border-radius: 8px;
    padding: 6px;
}

/* ============================================================================
   6. PRO DATA TABLE VIEW
   ============================================================================ */
QTableView {
    background-color: rgba(11, 17, 32, 0.85);
    color: #f1f5f9;
    gridline-color: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 10px;
    selection-background-color: rgba(30, 58, 138, 0.60);
    selection-color: #ffffff;
    outline: none;
    font-size: 14px;
}

QTableView::item {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

QTableView::item:hover {
    background-color: rgba(30, 41, 59, 0.50);
}

QTableView::item:selected {
    background-color: rgba(30, 58, 138, 0.70);
    color: #38bdf8;
}

QHeaderView::section {
    background-color: #080c16;
    color: #94a3b8;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid rgba(56, 189, 248, 0.35);
    border-right: 1px solid rgba(148, 163, 184, 0.08);
    border-top: none;
    border-left: none;
    padding: 12px 14px;
}

/* ============================================================================
   7. MODERN GLASS TABS
   ============================================================================ */
QTabWidget::pane {
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    background-color: rgba(11, 17, 32, 0.80);
    padding: 16px;
}

QTabBar::tab {
    background-color: rgba(15, 23, 42, 0.70);
    color: #94a3b8;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 20px;
    margin-right: 6px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-bottom: none;
}

QTabBar::tab:hover {
    background-color: rgba(30, 41, 59, 0.85);
    color: #f1f5f9;
}

QTabBar::tab:selected {
    background-color: rgba(11, 17, 32, 0.95);
    color: #38bdf8;
    font-weight: 700;
    border: 1px solid rgba(56, 189, 248, 0.40);
    border-bottom: 2px solid #38bdf8;
}

/* ============================================================================
   8. STATUS BAR, TOOLBAR & SCROLLBARS
   ============================================================================ */
QToolBar {
    background-color: rgba(10, 15, 29, 0.95);
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    padding: 8px 14px;
    spacing: 10px;
}

QToolButton {
    background-color: rgba(30, 41, 59, 0.60);
    color: #f1f5f9;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

QToolButton:hover {
    background-color: rgba(51, 65, 85, 0.80);
    border-color: rgba(56, 189, 248, 0.45);
}

QStatusBar {
    background-color: rgba(7, 10, 18, 0.95);
    color: #64748b;
    border-top: 1px solid rgba(148, 163, 184, 0.12);
    font-size: 13px;
    padding: 6px 12px;
}

QScrollBar:vertical {
    border: none;
    background: rgba(15, 23, 42, 0.40);
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(148, 163, 184, 0.25);
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(56, 189, 248, 0.50);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: rgba(15, 23, 42, 0.40);
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: rgba(148, 163, 184, 0.25);
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(56, 189, 248, 0.50);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QSplitter::handle {
    background-color: rgba(148, 163, 184, 0.15);
    width: 3px;
}

QSplitter::handle:hover {
    background-color: #38bdf8;
}
"""


def get_badge_qss(severity: str) -> str:
    """Returns CSS style string for colored glassmorphism severity pills without emojis."""
    sev = severity.lower()
    if sev in ("critical", "block", "high", "error"):
        return """
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.45);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
        """
    elif sev in ("warning", "warn", "medium"):
        return """
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.45);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
        """
    elif sev in ("ok", "verified", "approved", "reviewed", "low"):
        return """
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.45);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
        """
    else:  # info / default
        return """
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.45);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
        """
