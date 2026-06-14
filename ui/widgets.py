import os
from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QAbstractItemView, QMenu, QAction, QFrame,
)
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor
from ui.theme import TEXT, TEXT_SEC, BG_CARD, BG_HOVER, BORDER, TEXT_DIM

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
