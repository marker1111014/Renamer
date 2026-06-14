from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from ui.theme import BG_DEEP, BG_CARD, TEXT, TEXT_SEC, TEXT_DIM, BORDER, BG_ALT, S_BTN_FLAT, S_BTN_PRIMARY, S_TABLE


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
