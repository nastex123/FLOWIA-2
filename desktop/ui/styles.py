"""Gothic Cyber-Obsidian Design System and Stylesheet for FlowMind AI Desktop."""

DARK_THEME_QSS = """
/* ============================================================================
   1. GOTHIC OBSIDIAN GLOBAL WINDOW & TYPOGRAPHY
   ============================================================================ */
QMainWindow {
    background-color: #030408;
    color: #f1f5f9;
    font-family: "Georgia", "Palatino Linotype", "Garamond", "Times New Roman", -apple-system, sans-serif;
}

QDialog {
    background-color: #06050b;
    color: #f8fafc;
    border: 1px solid rgba(225, 29, 72, 0.45);
    border-radius: 10px;
    font-family: "Georgia", "Segoe UI", sans-serif;
}

QWidget {
    color: #e2e8f0;
    font-size: 14px;
    font-family: "Segoe UI", "Georgia", sans-serif;
}

/* ============================================================================
   2. GOTHIC GLASSMORPHISM CARDS & PANELS (Crimson & Obsidian)
   ============================================================================ */
QFrame#glassCard, QFrame#card {
    background-color: rgba(12, 10, 20, 0.82);
    border: 1px solid rgba(136, 19, 55, 0.35);
    border-radius: 10px;
    padding: 16px;
}

QFrame#glassCard:hover, QFrame#card:hover {
    border: 1px solid rgba(225, 29, 72, 0.70);
    background-color: rgba(19, 13, 28, 0.90);
}

QFrame#kpiCard {
    background-color: rgba(15, 11, 24, 0.85);
    border: 1px solid rgba(159, 18, 57, 0.35);
    border-radius: 10px;
    padding: 16px 18px;
}

QFrame#kpiCard:hover {
    background-color: rgba(28, 17, 43, 0.95);
    border: 1px solid rgba(244, 63, 94, 0.85);
}

QFrame#glassPanel {
    background-color: rgba(10, 8, 17, 0.90);
    border: 1px solid rgba(88, 28, 135, 0.30);
    border-radius: 10px;
    padding: 18px;
}

QFrame#actionBar {
    background-color: rgba(15, 10, 24, 0.95);
    border-top: 1px solid rgba(225, 29, 72, 0.40);
    padding: 14px 22px;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}

/* ============================================================================
   3. GOTHIC SIDEBAR NAVIGATION
   ============================================================================ */
QWidget#sidebarContainer {
    background-color: rgba(6, 4, 11, 0.98);
    border-right: 1px solid rgba(136, 19, 55, 0.30);
}

QListWidget#sidebar {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    padding: 14px 8px;
    outline: none;
}

QListWidget#sidebar::item {
    padding: 12px 16px;
    margin-bottom: 6px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    color: #94a3b8;
    border-left: 2px solid transparent;
}

QListWidget#sidebar::item:hover {
    background-color: rgba(28, 15, 38, 0.80);
    color: #fda4af;
    border-left: 2px solid rgba(225, 29, 72, 0.65);
}

QListWidget#sidebar::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(136, 19, 55, 0.85), stop:1 rgba(30, 10, 30, 0.40));
    color: #ffe4e6;
    font-weight: 700;
    border-left: 4px solid #e11d48;
}

QPushButton#sidebarToggle {
    background-color: rgba(24, 15, 34, 0.80);
    color: #fda4af;
    border: 1px solid rgba(136, 19, 55, 0.40);
    border-radius: 6px;
    font-size: 16px;
    font-weight: bold;
    padding: 6px 10px;
    min-width: 36px;
    min-height: 36px;
}

QPushButton#sidebarToggle:hover {
    background-color: rgba(136, 19, 55, 0.40);
    color: #ffffff;
    border-color: rgba(225, 29, 72, 0.80);
}

/* ============================================================================
   4. GOTHIC BUTTONS (Crimson, Amethyst & Brass)
   ============================================================================ */
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #881337, stop:1 #4c0519);
    color: #fff1f2;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 22px;
    border-radius: 6px;
    border: 1px solid rgba(225, 29, 72, 0.45);
    min-height: 24px;
    letter-spacing: 0.3px;
}

QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #be123c, stop:1 #881337);
    border-color: rgba(251, 113, 133, 0.90);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #4c0519;
}

QPushButton:disabled {
    background-color: rgba(20, 15, 28, 0.60);
    color: #584c63;
    border-color: rgba(88, 28, 135, 0.20);
}

QPushButton#secondaryButton {
    background-color: rgba(26, 18, 38, 0.85);
    color: #cbd5e1;
    border: 1px solid rgba(136, 19, 55, 0.30);
}

QPushButton#secondaryButton:hover {
    background-color: rgba(45, 25, 60, 0.95);
    color: #ffffff;
    border-color: rgba(225, 29, 72, 0.60);
}

QPushButton#successButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #064e3b, stop:1 #022c22);
    color: #ecfdf5;
    border: 1px solid rgba(16, 185, 129, 0.50);
    font-size: 14px;
    font-weight: 700;
    padding: 12px 24px;
    letter-spacing: 0.5px;
}

QPushButton#successButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #064e3b);
    border-color: rgba(52, 211, 153, 0.90);
    color: #ffffff;
}

/* Chip Filter Buttons */
QPushButton#chipFilter {
    background-color: rgba(20, 14, 30, 0.80);
    color: #94a3b8;
    border: 1px solid rgba(136, 19, 55, 0.30);
    border-radius: 16px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton#chipFilter:hover {
    background-color: rgba(40, 20, 50, 0.90);
    color: #fce7f3;
    border-color: rgba(225, 29, 72, 0.60);
}

QPushButton#chipFilter[active="true"] {
    background-color: rgba(136, 19, 55, 0.35);
    color: #fda4af;
    border: 1px solid #e11d48;
}

/* ============================================================================
   5. GOTHIC INPUTS & COMBOBOXES
   ============================================================================ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: rgba(10, 8, 18, 0.92);
    color: #f8fafc;
    border: 1px solid rgba(136, 19, 55, 0.35);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #881337;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #e11d48;
    background-color: rgba(15, 10, 25, 0.98);
}

QComboBox {
    background-color: rgba(10, 8, 18, 0.92);
    color: #f8fafc;
    border: 1px solid rgba(136, 19, 55, 0.35);
    border-radius: 6px;
    padding: 9px 14px;
    min-height: 24px;
    font-size: 14px;
}

QComboBox:focus {
    border: 1px solid #e11d48;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #0b0814;
    color: #f8fafc;
    border: 1px solid rgba(225, 29, 72, 0.45);
    selection-background-color: #4c0519;
    selection-color: #fda4af;
    border-radius: 6px;
    padding: 6px;
}

/* ============================================================================
   6. GOTHIC TABLE VIEW (Crypt Theme)
   ============================================================================ */
QTableView {
    background-color: rgba(8, 6, 14, 0.90);
    color: #f1f5f9;
    gridline-color: rgba(136, 19, 55, 0.15);
    border: 1px solid rgba(136, 19, 55, 0.25);
    border-radius: 8px;
    selection-background-color: rgba(136, 19, 55, 0.50);
    selection-color: #ffffff;
    outline: none;
    font-size: 14px;
}

QTableView::item {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(88, 28, 135, 0.12);
}

QTableView::item:hover {
    background-color: rgba(28, 15, 40, 0.60);
}

QTableView::item:selected {
    background-color: rgba(136, 19, 55, 0.65);
    color: #ffe4e6;
}

QHeaderView::section {
    background-color: #050308;
    color: #cbd5e1;
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 2px solid #881337;
    border-right: 1px solid rgba(136, 19, 55, 0.18);
    border-top: none;
    border-left: none;
    padding: 12px 14px;
}

/* ============================================================================
   7. CATHEDRAL TABS
   ============================================================================ */
QTabWidget::pane {
    border: 1px solid rgba(136, 19, 55, 0.30);
    border-radius: 10px;
    background-color: rgba(10, 8, 17, 0.88);
    padding: 16px;
}

QTabBar::tab {
    background-color: rgba(15, 10, 24, 0.85);
    color: #94a3b8;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 22px;
    margin-right: 6px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid rgba(136, 19, 55, 0.25);
    border-bottom: none;
    letter-spacing: 0.3px;
}

QTabBar::tab:hover {
    background-color: rgba(28, 17, 43, 0.95);
    color: #fda4af;
}

QTabBar::tab:selected {
    background-color: rgba(10, 8, 17, 0.98);
    color: #f43f5e;
    font-weight: 700;
    border: 1px solid rgba(225, 29, 72, 0.55);
    border-bottom: 2px solid #e11d48;
}

/* ============================================================================
   8. STATUS BAR, TOOLBAR & SCROLLBARS
   ============================================================================ */
QToolBar {
    background-color: rgba(6, 4, 11, 0.98);
    border-bottom: 1px solid rgba(136, 19, 55, 0.25);
    padding: 8px 14px;
    spacing: 10px;
}

QToolButton {
    background-color: rgba(22, 14, 32, 0.80);
    color: #f1f5f9;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 14px;
    border-radius: 6px;
    border: 1px solid rgba(136, 19, 55, 0.30);
}

QToolButton:hover {
    background-color: rgba(45, 22, 60, 0.90);
    border-color: rgba(225, 29, 72, 0.65);
    color: #ffffff;
}

QStatusBar {
    background-color: rgba(4, 3, 7, 0.98);
    color: #64748b;
    border-top: 1px solid rgba(136, 19, 55, 0.20);
    font-size: 13px;
    padding: 6px 12px;
}

QScrollBar:vertical {
    border: none;
    background: rgba(10, 8, 16, 0.50);
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(136, 19, 55, 0.40);
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(225, 29, 72, 0.80);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: rgba(10, 8, 16, 0.50);
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: rgba(136, 19, 55, 0.40);
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(225, 29, 72, 0.80);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QSplitter::handle {
    background-color: rgba(136, 19, 55, 0.25);
    width: 3px;
}

QSplitter::handle:hover {
    background-color: #e11d48;
}
"""


def get_badge_qss(severity: str) -> str:
    """Returns CSS style string for gothic severity pills without emojis."""
    sev = severity.lower()
    if sev in ("critical", "block", "high", "error"):
        return """
            background-color: rgba(159, 18, 57, 0.25);
            color: #fb7185;
            border: 1px solid rgba(225, 29, 72, 0.65);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        """
    elif sev in ("warning", "warn", "medium"):
        return """
            background-color: rgba(180, 83, 9, 0.25);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.65);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        """
    elif sev in ("ok", "verified", "approved", "reviewed", "low"):
        return """
            background-color: rgba(6, 78, 59, 0.25);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.65);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        """
    else:  # info / default
        return """
            background-color: rgba(88, 28, 135, 0.25);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.65);
            border-radius: 12px;
            padding: 3px 10px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        """
