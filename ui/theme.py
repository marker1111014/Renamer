import os
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QFont
from PyQt5.QtCore import QByteArray

BG_DEEP = "#1E1E1E"
BG_CARD = "#2D2D2D"
BG_ALT = "#333333"
BG_HOVER = "#3D3D3D"
BORDER = "#4A4A4A"
BORDER_FOCUS = "#0078D7"
TEXT = "#E8E8E8"
TEXT_SEC = "#B8B8B8"
TEXT_DIM = "#8A8A8A"
ACCENT = "#0078D7"
ACCENT_HVR = "#1A8AD4"
DANGER = "#E81123"

FONT = "Microsoft JhengHei UI, Segoe UI, Noto Sans CJK TC, sans-serif"

S_BASE = f"""
QWidget {{
    font-family: "{FONT}";
    font-size: 14px;
    color: {TEXT};
    background-color: {BG_DEEP};
}}
QToolTip {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 6px 10px;
    border-radius: 3px;
    font-size: 13px;
}}
"""

S_LIST = f"""
QListWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 6px;
    outline: none;
    font-size: 14px;
}}
QListWidget::item {{
    padding: 10px 14px;
    border-radius: 4px;
    margin: 1px 2px;
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: {ACCENT};
    color: white;
}}
QListWidget::item:hover:!selected {{
    background-color: {BG_HOVER};
}}
QListWidget::item:selected:hover {{
    background-color: {ACCENT_HVR};
}}
QListWidget::drop-indicator {{
    height: 3px;
    background-color: {ACCENT};
    border-radius: 1px;
}}
QListWidget::disabled {{
    background-color: {BG_DEEP};
}}
"""

S_BTN_FLAT = f"""
QPushButton {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 8px 18px;
    font-size: 14px;
    color: {TEXT};
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: #555;
}}
QPushButton:pressed {{
    background-color: #3A3A3A;
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
}}
"""

S_BTN_PRIMARY = f"""
QPushButton {{
    background-color: {ACCENT};
    border: none;
    border-radius: 4px;
    padding: 8px 28px;
    font-size: 14px;
    font-weight: 600;
    color: white;
}}
QPushButton:hover {{
    background-color: {ACCENT_HVR};
}}
QPushButton:pressed {{
    background-color: #0060B3;
}}
QPushButton:disabled {{
    background-color: #3A3A3A;
    color: {TEXT_DIM};
}}
"""

S_INPUT = f"""
QLineEdit, QSpinBox {{
    background-color: {BG_DEEP};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 14px;
    color: {TEXT};
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {ACCENT};
}}
QLineEdit:hover:!focus, QSpinBox:hover:!focus {{
    border-color: #555;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-left: none;
    width: 24px;
    border-radius: 2px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {BG_HOVER};
    border-color: {ACCENT};
}}
QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
    background-color: #444;
}}
QSpinBox::up-arrow {{
    width: 8px;
    height: 8px;
    border: 2px solid {TEXT_SEC};
    border-bottom: none;
    border-right: none;
    transform: rotate(45deg);
    margin-bottom: 2px;
}}
QSpinBox::down-arrow {{
    width: 8px;
    height: 8px;
    border: 2px solid {TEXT_SEC};
    border-top: none;
    border-left: none;
    transform: rotate(45deg);
    margin-top: 2px;
}}
"""

S_CHECKBOX = f"""
QCheckBox {{
    spacing: 8px;
    font-size: 14px;
    color: {TEXT};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {BG_DEEP};
}}
QCheckBox::indicator:hover {{
    border-color: #555;
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
QCheckBox::indicator:checked:hover {{
    background-color: {ACCENT_HVR};
    border-color: {ACCENT_HVR};
}}
"""

S_TABLE = f"""
QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    gridline-color: {BORDER};
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 6px 10px;
    color: {TEXT};
}}
QHeaderView::section {{
    background-color: {BG_ALT};
    color: {TEXT_SEC};
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
    font-size: 13px;
}}
"""

S_HEADER = f"QLabel {{ font-size: 14px; color: {TEXT_SEC}; }}"
S_STATUS = f"QLabel {{ font-size: 13px; color: #9C9C9C; }}"


def setup_palette(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BG_DEEP))
    palette.setColor(QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Base, QColor(BG_CARD))
    palette.setColor(QPalette.AlternateBase, QColor(BG_ALT))
    palette.setColor(QPalette.Button, QColor(BG_CARD))
    palette.setColor(QPalette.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipBase, QColor(BG_CARD))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.PlaceholderText, QColor("#9A9A9A"))
    app.setPalette(palette)

    font = QFont(FONT, 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)


def make_icon():
    ico_path = os.path.join(os.path.dirname(__file__), "..", "favicon.ico")
    if os.path.exists(ico_path):
        return QIcon(ico_path)

    b64_path = os.path.join(os.path.dirname(__file__), "..", "icon_b64.txt")
    if os.path.exists(b64_path):
        with open(b64_path, "r") as f:
            data = f.read()
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray.fromBase64(data.encode()))
        return QIcon(pixmap)

    return QIcon()
