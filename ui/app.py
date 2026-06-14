import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSpinBox, QLabel, QMessageBox,
    QLineEdit, QCheckBox, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from core.naming import compute_new_name
from core.operations import build_rename_entries, execute_rename, ConflictAction
from ui.theme import (
    BG_DEEP, BG_CARD, TEXT, TEXT_SEC, TEXT_DIM, BORDER,
    S_BASE, S_LIST, S_BTN_FLAT, S_BTN_PRIMARY, S_INPUT, S_CHECKBOX,
    S_HEADER, S_STATUS,
)
from ui.widgets import DropListWidget, FLAG_SKIP_STRIP, FLAG_SKIP_PREFIX
from ui.preview import PreviewDialog


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
        opt_container = QVBoxLayout()
        opt_container.setSpacing(8)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        dl = QLabel("刪除前綴字數")
        dl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        row1.addWidget(dl)
        self.strip_spin = QSpinBox()
        self.strip_spin.setRange(0, 999)
        self.strip_spin.setValue(0)
        self.strip_spin.setFixedWidth(70)
        self.strip_spin.setStyleSheet(S_INPUT)
        row1.addWidget(self.strip_spin)

        self.strip_all_check = QCheckBox("全刪")
        self.strip_all_check.setStyleSheet(S_CHECKBOX)
        self.strip_all_check.toggled.connect(self._on_strip_all_toggled)
        row1.addWidget(self.strip_all_check)

        row1.addSpacing(18)

        pl = QLabel("前置詞")
        pl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        row1.addWidget(pl)
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("可留空")
        self.prefix_edit.setMaximumWidth(130)
        self.prefix_edit.setStyleSheet(S_INPUT)
        row1.addWidget(self.prefix_edit)

        row1.addStretch()
        opt_container.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        sl = QLabel("起始數字")
        sl.setStyleSheet(f"font-size: 14px; color: {TEXT_SEC};")
        row2.addWidget(sl)
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 999999)
        self.start_spin.setValue(1)
        self.start_spin.setFixedWidth(100)
        self.start_spin.setStyleSheet(S_INPUT)
        row2.addWidget(self.start_spin)
        row2.addSpacing(10)

        self.auto_pad_check = QCheckBox("自動補零")
        self.auto_pad_check.setChecked(True)
        self.auto_pad_check.setStyleSheet(S_CHECKBOX)
        row2.addWidget(self.auto_pad_check)

        row2.addStretch()
        opt_container.addLayout(row2)

        c.addLayout(opt_container)

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

    def _on_strip_all_toggled(self, checked):
        self.strip_spin.setEnabled(not checked)

    def _on_item_changed(self, item):
        item.setForeground(QColor(TEXT) if item.checkState() == Qt.Checked else QColor(TEXT_SEC))
        DropListWidget._refresh_item_text(item)
        self.update_status()

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

    def rename_files(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, "警告", "請先加入要重新命名的檔案")
            return

        total = self.list_widget.count()
        strip = self.strip_spin.value()
        prefix_val = self.prefix_edit.text().strip()
        start = self.start_spin.value()
        auto_pad = self.auto_pad_check.isChecked()
        strip_all = self.strip_all_check.isChecked()

        file_paths = []
        new_names = []
        item_map = {}

        for i in range(total):
            item = self.list_widget.item(i)
            fp = item.data(Qt.UserRole)
            if not fp or not os.path.exists(fp):
                continue

            skip_strip = (item.checkState() == Qt.Unchecked
                          and item.data(FLAG_SKIP_STRIP))
            skip_prefix = (item.checkState() == Qt.Unchecked
                           and item.data(FLAG_SKIP_PREFIX))

            new_name, _ = compute_new_name(
                fp, i, total,
                strip=strip, prefix=prefix_val, start=start, auto_pad=auto_pad,
                skip_strip=skip_strip, skip_prefix=skip_prefix,
                strip_all=strip_all,
            )
            file_paths.append(fp)
            new_names.append(new_name)
            item_map[fp] = (item, new_name)

        if not file_paths:
            QMessageBox.warning(self, "警告", "沒有有效的檔案可供重新命名")
            return

        preview_data = [(os.path.basename(fp), nn) for fp, nn in zip(file_paths, new_names)]
        dialog = PreviewDialog(preview_data, self)
        if not dialog.exec_():
            return

        entries = build_rename_entries(file_paths, new_names)
        result = execute_rename(entries, conflict_handler=self._handle_conflict)

        for orig_path, actual_new_name in result.successes:
            item, _ = item_map.get(orig_path, (None, None))
            if item is not None:
                new_full_path = os.path.join(os.path.dirname(orig_path), actual_new_name)
                item.setData(Qt.UserRole, new_full_path)
                item.setText(actual_new_name)

        msg_parts = [f"成功重新命名 {len(result.successes)} 個檔案"]
        if result.skipped:
            msg_parts.append(f"{len(result.skipped)} 個跳過")
        if result.errors:
            msg_parts.append(f"{len(result.errors)} 個失敗")
        QMessageBox.information(self, "完成", "，".join(msg_parts))

    def _handle_conflict(self, new_path, new_name):
        reply = QMessageBox.question(
            self, "檔案已存在",
            f"「{new_name}」已存在，是否覆蓋？\n"
            f"按「否」可跳過此檔案，按「取消」終止操作。",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            return ConflictAction.OVERWRITE
        elif reply == QMessageBox.Cancel:
            return ConflictAction.CANCEL
        return ConflictAction.SKIP
