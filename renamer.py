import sys
import os
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QSpinBox, QLabel, QMessageBox,
                             QAbstractItemView, QLineEdit, QCheckBox, QFrame,
                             QSizePolicy, QButtonGroup, QDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractScrollArea,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, QByteArray, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon, QPalette, QColor, QPixmap

# ── Dark palette ──────────────────────────────────────────────────
BG_DEEP    = "#1E1E1E"
BG_CARD    = "#2D2D2D"
BG_ALT     = "#333333"
BG_HOVER   = "#3D3D3D"
BORDER     = "#4A4A4A"
BORDER_FOCUS = "#0078D7"
TEXT       = "#E8E8E8"
TEXT_SEC   = "#B8B8B8"
TEXT_DIM   = "#8A8A8A"
ACCENT     = "#0078D7"
ACCENT_HVR = "#1A8AD4"
DANGER     = "#E81123"

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

S_HEADER = f"QLabel {{ font-size: 14px; color: {TEXT_SEC}; }}"
S_STATUS = f"QLabel {{ font-size: 13px; color: #9C9C9C; }}"

FLAG_SKIP_STRIP = Qt.UserRole + 1
FLAG_SKIP_PREFIX = Qt.UserRole + 2
ORIG_NAME_ROLE = Qt.UserRole + 3


class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    exists = False
                    for i in range(self.count()):
                        if self.item(i).data(Qt.UserRole) == file_path:
                            exists = True
                            break
                    if not exists:
                        item = QListWidgetItem()
                        item.setData(Qt.UserRole, file_path)
                        item.setData(ORIG_NAME_ROLE, os.path.basename(file_path))
                        item.setData(FLAG_SKIP_STRIP, False)
                        item.setData(FLAG_SKIP_PREFIX, False)
                        item.setSizeHint(QSize(0, 38))
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                        item.setCheckState(Qt.Checked)
                        self._refresh_item_text(item)
                        self.addItem(item)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    @staticmethod
    def _refresh_item_text(item):
        name = item.data(ORIG_NAME_ROLE) or os.path.basename(item.data(Qt.UserRole) or "")
        tags = []
        if item.data(FLAG_SKIP_PREFIX):
            tags.append("略過前置")
        if item.data(FLAG_SKIP_STRIP):
            tags.append("略過刪除")
        suffix = f"  ⚲{', '.join(tags)}" if tags else ""
        item.setText(f"{name}{suffix}")

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            return
        self.setCurrentItem(item)
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                color: {TEXT};
            }}
            QMenu::item {{
                padding: 8px 28px 8px 12px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: {BG_HOVER};
                color: {TEXT};
            }}
            QMenu::item:disabled {{
                color: {TEXT_DIM};
            }}
            QMenu::indicator {{
                width: 16px;
                height: 16px;
                margin-right: 6px;
            }}
        """)

        act_prefix = QAction("套用前置詞", self)
        act_prefix.setCheckable(True)
        act_prefix.setChecked(not (item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_PREFIX)))
        act_prefix.triggered.connect(lambda checked, it=item: self._toggle_flag(it, FLAG_SKIP_PREFIX, checked))
        menu.addAction(act_prefix)

        act_strip = QAction("套用刪除前綴", self)
        act_strip.setCheckable(True)
        act_strip.setChecked(not (item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_STRIP)))
        act_strip.triggered.connect(lambda checked, it=item: self._toggle_flag(it, FLAG_SKIP_STRIP, checked))
        menu.addAction(act_strip)

        menu.addSeparator()

        act_remove = QAction("移除此檔案", self)
        act_remove.triggered.connect(lambda _, it=item: self._remove_item(it))
        menu.addAction(act_remove)

        menu.exec_(event.globalPos())

    def _toggle_flag(self, item, flag_role, enabled):
        if enabled:
            item.setData(flag_role, False)
            if not item.data(FLAG_SKIP_STRIP) and not item.data(FLAG_SKIP_PREFIX):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Unchecked)
            item.setData(flag_role, True)
        item.setForeground(QColor(TEXT) if item.checkState() == Qt.Checked else QColor(TEXT_SEC))
        self._refresh_item_text(item)

    def _remove_item(self, item):
        self.takeItem(self.row(item))

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


class PreviewDialog(QDialog):
    def __init__(self, preview_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("重新命名預覽")
        self.setMinimumSize(580, 360)
        self.resize(640, 420)
        self.setStyleSheet(f"background-color: {BG_DEEP};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(f"將重新命名以下 {len(preview_data)} 個檔案：")
        title.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT};")
        layout.addWidget(title)

        table = QTableWidget(len(preview_data), 3)
        table.setHorizontalHeaderLabels(["#", "原始檔名", "新檔名"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setShowGrid(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setStyleSheet(S_TABLE)

        changed_count = 0
        for row, (old_name, new_name) in enumerate(preview_data):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, num_item)

            old_item = QTableWidgetItem(old_name)
            old_item.setForeground(QColor(TEXT_SEC))
            table.setItem(row, 1, old_item)

            new_item = QTableWidgetItem(new_name)
            if old_name != new_name:
                new_item.setForeground(QColor("#4EC9B0"))
                changed_count += 1
            else:
                new_item.setForeground(QColor(TEXT_DIM))
            table.setItem(row, 2, new_item)

        layout.addWidget(table)

        info = QLabel(f"其中 {changed_count} 個檔案名稱將被變更")
        info.setStyleSheet(f"font-size: 13px; color: {TEXT_SEC};")
        layout.addWidget(info)

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(S_BTN_FLAT)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        confirm_btn = QPushButton("確認執行")
        confirm_btn.setStyleSheet(S_BTN_PRIMARY)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        buttons.addWidget(confirm_btn)

        layout.addLayout(buttons)


class RenamerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("重新命名工具")
        self.setGeometry(100, 100, 680, 560)
        self.setMinimumSize(520, 420)

        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background-color: {BG_DEEP};")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        h = QVBoxLayout(header)
        h.setContentsMargins(28, 22, 28, 18)
        h.setSpacing(4)

        t = QLabel("重新命名工具")
        t.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 600;
                color: {TEXT};
            }}
        """)
        h.addWidget(t)

        d = QLabel("拖曳檔案到下方列表，右鍵可個別設定「前置詞」「刪除前綴」規則")
        d.setStyleSheet(S_HEADER)
        h.addWidget(d)
        root.addWidget(header)

        # ── Content ───────────────────────────────────────────
        c = QVBoxLayout()
        c.setContentsMargins(28, 18, 28, 18)
        c.setSpacing(14)

        self.list_widget = DropListWidget()
        self.list_widget.setStyleSheet(S_LIST)
        c.addWidget(self.list_widget, 1)

        # ── Options ───────────────────────────────────────────
        o = QHBoxLayout()
        o.setSpacing(10)

        dl = QLabel("刪除前綴字數")
        dl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        o.addWidget(dl)
        self.strip_spin = QSpinBox()
        self.strip_spin.setRange(0, 99)
        self.strip_spin.setValue(0)
        self.strip_spin.setFixedWidth(70)
        self.strip_spin.setStyleSheet(S_INPUT)
        o.addWidget(self.strip_spin)
        o.addSpacing(18)

        pl = QLabel("前置詞")
        pl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        o.addWidget(pl)
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("可留空")
        self.prefix_edit.setMaximumWidth(130)
        self.prefix_edit.setStyleSheet(S_INPUT)
        o.addWidget(self.prefix_edit)
        o.addSpacing(18)

        sl = QLabel("起始數字")
        sl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        o.addWidget(sl)
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 999999)
        self.start_spin.setValue(1)
        self.start_spin.setFixedWidth(100)
        self.start_spin.setStyleSheet(S_INPUT)
        o.addWidget(self.start_spin)
        o.addSpacing(10)

        self.auto_pad_check = QCheckBox("自動補零")
        self.auto_pad_check.setChecked(True)
        self.auto_pad_check.setStyleSheet(S_CHECKBOX)
        o.addWidget(self.auto_pad_check)

        o.addStretch()
        c.addLayout(o)

        # ── Buttons ───────────────────────────────────────────
        b = QHBoxLayout()
        b.setSpacing(10)

        self.btn_remove = QPushButton("移除選取")
        self.btn_remove.setStyleSheet(S_BTN_FLAT)
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.clicked.connect(self.remove_selected)
        b.addWidget(self.btn_remove)

        self.btn_clear = QPushButton("清空列表")
        self.btn_clear.setStyleSheet(S_BTN_FLAT)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_list)
        b.addWidget(self.btn_clear)

        b.addStretch()

        self.btn_rename = QPushButton("開始重新命名")
        self.btn_rename.setStyleSheet(S_BTN_PRIMARY)
        self.btn_rename.setCursor(Qt.PointingHandCursor)
        self.btn_rename.clicked.connect(self.rename_files)
        b.addWidget(self.btn_rename)
        c.addLayout(b)

        root.addLayout(c)

        # ── Status bar ────────────────────────────────────────
        sb = QFrame()
        sb.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-top: 1px solid {BORDER};
            }}
        """)
        sbl = QHBoxLayout(sb)
        sbl.setContentsMargins(28, 8, 28, 8)

        self.status_label = QLabel("尚未加入任何檔案 — 從檔案總管拖曳檔案到上方區域")
        self.status_label.setStyleSheet(S_STATUS)
        sbl.addWidget(self.status_label)

        sbl.addStretch()

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(S_STATUS)
        sbl.addWidget(self.count_label)

        root.addWidget(sb)

        # Signals
        self.list_widget.model().rowsInserted.connect(self.update_status)
        self.list_widget.model().rowsRemoved.connect(self.update_status)
        self.list_widget.itemChanged.connect(self._on_item_changed)

    def update_status(self):
        count = self.list_widget.count()
        if count == 0:
            self.status_label.setText("尚未加入任何檔案 — 從檔案總管拖曳檔案到上方區域")
        else:
            n_strip = sum(1 for i in range(count)
                          if self.list_widget.item(i).checkState() == Qt.Unchecked
                          and self.list_widget.item(i).data(FLAG_SKIP_STRIP))
            n_prefix = sum(1 for i in range(count)
                           if self.list_widget.item(i).checkState() == Qt.Unchecked
                           and self.list_widget.item(i).data(FLAG_SKIP_PREFIX))
            parts = [f"已加入 {count} 個檔案"]
            if n_strip:
                parts.append(f"{n_strip} 個不刪除前綴")
            if n_prefix:
                parts.append(f"{n_prefix} 個不加前置詞")
            parts.append("確認順序無誤後點擊「開始重新命名」")
            self.status_label.setText("  |  ".join(parts))

    def _on_item_changed(self, item):
        item.setForeground(QColor(TEXT) if item.checkState() == Qt.Checked else QColor(TEXT_SEC))
        self._refresh_item_text(item)
        self.update_status()

    def _refresh_item_text(self, item):
        DropListWidget._refresh_item_text(item)

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def clear_list(self):
        if self.list_widget.count() == 0:
            return
        reply = QMessageBox.question(
            self, "清空列表",
            "確定要清空所有已加入的檔案？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.list_widget.clear()

    def _compute_new_name(self, file_path, index, total_count, item=None):
        skip_strip = item is not None and item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_STRIP)
        skip_prefix = item is not None and item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_PREFIX)

        start = self.start_spin.value()
        prefix = "" if skip_prefix else self.prefix_edit.text().strip()
        strip = self.strip_spin.value()
        raw = len(str(start + total_count - 1)) if total_count else 1
        pad = max(2, raw) if self.auto_pad_check.isChecked() else 0

        name, ext = os.path.splitext(os.path.basename(file_path))
        remaining = name if skip_strip else (name[strip:] if strip < len(name) else "")
        num = f"{start + index:0{pad}d}" if pad else str(start + index)
        new_name = f"{prefix}{num}{remaining}{ext}"
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        return new_name, new_path

    def _build_preview_data(self):
        data = []
        total = self.list_widget.count()
        for i in range(total):
            item = self.list_widget.item(i)
            file_path = item.data(Qt.UserRole)
            if not file_path:
                continue
            old_name = os.path.basename(file_path)
            new_name, _ = self._compute_new_name(file_path, i, total, item)
            data.append((old_name, new_name))
        return data

    def rename_files(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, "警告", "請先加入要重新命名的檔案")
            return

        preview_data = self._build_preview_data()
        dialog = PreviewDialog(preview_data, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        start = self.start_spin.value()
        prefix = self.prefix_edit.text().strip()
        count = self.list_widget.count()
        strip = self.strip_spin.value()
        raw = len(str(start + count - 1)) if count else 1
        pad = max(2, raw) if self.auto_pad_check.isChecked() else 0

        temp_entries = []
        for i in range(count):
            item = self.list_widget.item(i)
            file_path = item.data(Qt.UserRole)
            if not file_path or not os.path.exists(file_path):
                continue

            dir_name = os.path.dirname(file_path)
            ext = os.path.splitext(file_path)[1]
            temp_name = f"__rename_tmp_{i}_{id(item)}{ext}"
            temp_path = os.path.join(dir_name, temp_name)

            try:
                os.rename(file_path, temp_path)
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法重新命名\n{file_path}\n{str(e)}")
                self._rollback(temp_entries)
                return
            temp_entries.append((temp_path, item, dir_name, ext))

        for i, (temp_path, item, dir_name, ext) in enumerate(temp_entries):
            skip_strip = item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_STRIP)
            skip_prefix = item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_PREFIX)
            base = os.path.basename(item.data(Qt.UserRole))
            name, _ = os.path.splitext(base)
            remaining = name if skip_strip else (name[strip:] if strip < len(name) else "")
            num = f"{start + i:0{pad}d}" if pad else str(start + i)
            new_name = f"{'' if skip_prefix else prefix}{num}{remaining}{ext}"
            new_path = os.path.join(dir_name, new_name)

            if os.path.exists(new_path):
                reply = QMessageBox.question(
                    self, "檔案已存在",
                    f"「{new_name}」已存在，是否覆蓋？\n"
                    f"按「否」可跳過此檔案，按「取消」終止操作。",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.No
                )
                if reply == QMessageBox.Cancel:
                    self._rollback(temp_entries[i:])
                    break
                elif reply == QMessageBox.No:
                    os.rename(temp_path, os.path.join(dir_name, f"_skipped_{new_name}"))
                    continue
                os.remove(new_path)

            try:
                os.rename(temp_path, new_path)
                item.setData(Qt.UserRole, new_path)
                item.setText(new_name)
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法重新命名\n{new_path}\n{str(e)}")
                self._rollback(temp_entries[i:])
                break

        QMessageBox.information(self, "完成", f"重新命名完成")

    def _rollback(self, temp_entries):
        for temp_path, item, dir_name, ext in temp_entries:
            if os.path.exists(temp_path):
                original = item.data(Qt.UserRole)
                if original and not os.path.exists(original):
                    try:
                        os.rename(temp_path, original)
                    except Exception:
                        pass


ICON_B64 = "AAABAAMAEBAAAAEAIABoBAAANgAAACAgAAABACAAqBAAAJ4EAAAwMAAAAQAgAKglAABGFQAAKAAAABAAAAAgAAAAAQAgAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAABLAAAAngAAAKcAAACnAAAApwAAAKcAAACnAAAApwAAAJ4AAABLAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAzAAAA4QAAAMEAAACnAAAApwAAAKcAAACnAAAApwAAAKcAAADBAAAA4QAAADMAAAAAAAAAAAAAAAAAAAAAAAAAXAAAAOMAAAAmAAAACwAAACAAAAAgAAAAIAAAACAAAAALAAAAJQAAAOIAAABaAAAAAAAAAAAAAAAAAAAAAAAAAF8AAADhAAAAHwAAAHkAAADiAAAA3wAAAN8AAADiAAAAeQAAAB0AAADeAAAAXQAAAAAAAAAAAAAAAAAAAAAAAABfAAAA4QAAACAAAAApAAAAWAAAAFgAAABYAAAAWAAAACkAAAAdAAAA3gAAAF0AAAAAAAAAAAAAAAAAAAAAAAAAXwAAAOEAAAAgAAAAKQAAAFgAAABYAAAAWAAAAFgAAAApAAAAHQAAAN4AAABdAAAAAAAAAAAAAAAAAAAAAAAAAF8AAADhAAAAHwAAAHkAAADiAAAA3wAAAN8AAADiAAAAeQAAAB0AAADeAAAAXQAAAAAAAAAAAAAAAAAAAAAAAABfAAAA4QAAACAAAAAKAAAAHwAAAB8AAAAfAAAAHgAAAAkAAAAdAAAA3gAAAF0AAAAAAAAAAAAAAAAAAAAAAAAAXwAAAOEAAAAhAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAcAAAAOQAAAOIAAABcAAAAAAAAAAAAAAAAAAAAAAAAAF8AAADhAAAAIQAAAAAAAAAAAAAAAAAAACYAAADAAAAA3wAAAOMAAAD4AAAAVQAAAAAAAAAAAAAAAAAAAAAAAABfAAAA4QAAACEAAAAAAAAAAAAAAAAAAABZAAAA6QAAAK4AAAD5AAAArwAAABcAAAAAAAAAAAAAAAAAAAAAAAAAXAAAAOQAAAAoAAAAAAAAAAIAAAAAAAAAXAAAAPQAAADoAAAArwAAABoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADMAAADiAAAAxAAAAKwAAACtAAAArAAAAMoAAAD/AAAAsAAAABoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAATAAAAJ8AAACpAAAAqQAAAKkAAACoAAAAigAAABsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAgAAAAIAAAACAAAAAgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADwDwAAwAMAAMADAADAAwAAwAMAAMADAADAAwAAwAMAAMADAADHgwAAxwMAAMcDAADFBwAAwA8AAMAfAADwPwAAKAAAACAAAABAAAAAAQAgAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEgAAAEMAAABYAAAAWQAAAFkAAABZAAAAWQAAAFkAAABZAAAAWQAAAFkAAABZAAAAWQAAAFkAAABZAAAAWAAAAEMAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD0AAADCAAAA9gAAAP0AAAD9AAAA/QAAAP0AAAD9AAAA/QAAAP0AAAD9AAAA/QAAAP0AAAD9AAAA/QAAAP0AAAD9AAAA9gAAAMIAAAA9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAAAA1QAAAP8AAAD/AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD/AAAA/wAAANQAAAAmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHkAAAD/AAAA/QAAAKgAAABcAAAAWgAAAFoAAABaAAAAWgAAAFoAAABaAAAAWgAAAFoAAABaAAAAWgAAAFoAAABaAAAAXAAAAKgAAAD+AAAA/wAAAHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAoAAAAP8AAADpAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKgAAAOcAAAD/AAAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAACqAAAA/wAAAOMAAAAiAAAAAAAAAAAAAAARAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAARAAAAAAAAAAAAAAAdAAAA3gAAAP8AAAClAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAKkAAAD/AAAA4wAAACMAAAAAAAAAJwAAAL8AAADiAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA4gAAAL8AAAAnAAAAAAAAAB0AAADeAAAA/wAAAKUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAqQAAAP8AAADjAAAAIwAAAAAAAABMAAAA+QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA+QAAAEwAAAAAAAAAHQAAAN4AAAD/AAAApQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAACpAAAA/wAAAOMAAAAjAAAAAAAAABEAAAB8AAAApgAAAKUAAAClAAAApQAAAKUAAAClAAAApQAAAKYAAAB8AAAAEQAAAAAAAAAdAAAA3gAAAP8AAAClAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAKkAAAD/AAAA4wAAACMAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAAAAAAAAAAAAAAAAB0AAADeAAAA/wAAAKUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAqQAAAP8AAADjAAAAIwAAAAAAAAAAAAAAAAAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAHQAAAN4AAAD/AAAApQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAACpAAAA/wAAAOMAAAAjAAAAAAAAABEAAAB8AAAApgAAAKUAAAClAAAApQAAAKUAAAClAAAApQAAAKYAAAB8AAAAEQAAAAAAAAAdAAAA3gAAAP8AAAClAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAKkAAAD/AAAA4wAAACMAAAAAAAAATAAAAPkAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPkAAABMAAAAAAAAAB0AAADeAAAA/wAAAKUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAqQAAAP8AAADjAAAAIwAAAAAAAAAnAAAAvwAAAOIAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADiAAAAvwAAACcAAAAAAAAAHQAAAN4AAAD/AAAApQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAACpAAAA/wAAAOMAAAAjAAAAAAAAAAAAAAARAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAARAAAAAAAAAAAAAAAdAAAA3gAAAP8AAAClAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAKkAAAD/AAAA4wAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADeAAAA/wAAAKUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAqQAAAP8AAADjAAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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gA/wf4Af8H+AH/B/AD/wfwB/8H8A//gAAf/4AAP//AAH//4AD////////////ygAAAAwAAAAYAAAAAEAIAAAAAAAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAGgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAGgAAAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFgAAAGoAAAC5AAAA2gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAAN4AAADeAAAA3gAAANoAAAC5AAAAagAAABUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKQAAALkAAAD8AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPwAAAC5AAAAKQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAALsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAALoAAAAXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHQAAAD+AAAA/wAAAP8AAAD+AAAA6wAAAOAAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA4AAAAOAAAADgAAAA6wAAAP4AAAD/AAAA/wAAAP4AAAByAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAL0AAAD/AAAA/wAAAP8AAACpAAAAMQAAAB4AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAfAAAAHwAAAB8AAAAeAAAAMQAAAKoAAAD/AAAA/wAAAP8AAAC+AAAACwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGgAAANgAAAD/AAAA/wAAAO0AAAA2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQAAADsAAAA/wAAAP8AAADbAAAAGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAQAAABQAAAAfAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB8AAAAUAAAAAQAAAAAAAAAAAAAAAAAAABwAAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAWAAAAM8AAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADPAAAAWAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAUAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAABQAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAUAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAABQAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAWAAAAM8AAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADPAAAAWAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAQAAABQAAAAfAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB8AAAAUAAAAAQAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAQAAABQAAAAfAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB8AAAAUAAAAAQAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAWAAAAM8AAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADPAAAAWAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAUAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAABQAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAUAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAABQAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAWAAAAM8AAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADPAAAAWAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAQAAABQAAAAfAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB4AAAAeAAAAHgAAAB8AAAAUAAAAAQAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADdAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAABoAAAAeAAAAHgAAAB4AAAAeAAAAHQAAADcAAADhAAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA7AAAArQAAANsAAADhAAAA4QAAAOEAAADhAAAA4AAAAOQAAAD7AAAA/wAAAP8AAADgAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgAAADcAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADhAAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAKYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADRAAAAFgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAANcAAAD/AAAA/wAAAPsAAADkAAAA4AAAAOIAAAD6AAAA/wAAAP8AAAD/AAAA/wAAAO8AAABhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOEAAAD/AAAA/wAAAOQAAAA4AAAAHQAAAH8AAAD3AAAA/wAAAP8AAAD/AAAA7wAAAGYAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOEAAAD/AAAA/wAAAOAAAAAgAAAAXQAAAOsAAAD/AAAA/wAAAP8AAADuAAAAZgAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJQAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOEAAAD/AAAA/wAAAOIAAAB/AAAA6gAAAP8AAAD/AAAA/wAAAO4AAABmAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAOQAAAD/AAAA/wAAAOQAAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOEAAAD/AAAA/wAAAPoAAAD2AAAA/wAAAP8AAAD/AAAA7gAAAGYAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGwAAANkAAAD/AAAA/wAAAO8AAAA5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADuAAAAZgAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAALwAAAD/AAAA/wAAAP8AAACtAAAAOAAAACcAAAAoAAAAKAAAACgAAAAoAAAAKAAAACgAAAAoAAAAKAAAACgAAAAmAAAAQQAAAOUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAO4AAABmAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHQAAAD+AAAA/wAAAP8AAAD+AAAA8AAAAOcAAADnAAAA5wAAAOcAAADnAAAA5wAAAOcAAADnAAAA5wAAAOcAAADnAAAA6gAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA7gAAAGYAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkAAAC+AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADuAAAAZgAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsAAAAuwAAAP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAO8AAABmAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFgAAAHAAAAC5AAAA1wAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADhAAAA4QAAAOEAAADjAAAA0gAAAGEAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAGQAAACEAAAAhAAAAIQAAACEAAAAhAAAAIQAAACEAAAAhAAAAIQAAACEAAAAhAAAAIQAAACEAAAAiAAAAFgAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////8AAP///////wAA////////AAD/8AAAD/8AAP/AAAAD/wAA/4AAAAH/AAD/AAAAAP8AAP8AAAAA/wAA/gAAAAB/AAD+B///4H8AAP4H///gfwAA/gcAAOB/AAD+BwAA4H8AAP4GAABgfwAA/gYAAGB/AAD+BwAA4H8AAP4HAADgfwAA/gf//+B/AAD+B///4H8AAP4HAADgfwAA/gcAAOB/AAD+BgAAYH8AAP4GAABgfwAA/gcAAOB/AAD+BwAA4H8AAP4H///gfwAA/gf//+B/AAD+B///4H8AAP4H///gfwAA/gf/8AB/AAD+B//gAH8AAP4H/8AAfwAA/gf/gAB/AAD+B/+AAP8AAP4H/4AA/wAA/gf/gAH/AAD+B/+AA/8AAP4H/4AH/wAA/gf/gA//AAD+AAAAH/8AAP8AAAA//wAA/wAAAH//AAD/gAAA//8AAP/AAAH//wAA//AAA///AAD///////8AAP///////wAA////////AAA="


def _make_icon():
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(ICON_B64.encode()))
    return QIcon(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(S_BASE)

    font = QFont(FONT, 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

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

    icon = _make_icon()
    app.setWindowIcon(icon)

    window = RenamerApp()
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
