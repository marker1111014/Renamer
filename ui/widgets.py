import os
import re
from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QAbstractItemView, QMenu, QAction, QFrame,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem, QApplication,
)
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QEvent
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor, QPainter, QFont, QKeySequence
from ui.theme import TEXT, TEXT_SEC, BG_CARD, BG_HOVER, BORDER, TEXT_DIM

FLAG_SKIP_STRIP = Qt.UserRole + 1
FLAG_SKIP_PREFIX = Qt.UserRole + 2
ORIG_NAME_ROLE = Qt.UserRole + 3
NEW_NAME_ROLE = Qt.UserRole + 4
IS_CONFLICT_ROLE = Qt.UserRole + 5


class RenameItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        return QSize(0, 36)

    def editorEvent(self, event, model, option, index):
        # 點擊左側核取方塊區域時切換選取狀態
        if event.type() in (QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
            if event.button() == Qt.LeftButton:
                check_rect = QRect(option.rect.left() + 8, option.rect.top() + (option.rect.height() - 16) // 2, 20, 18)
                if check_rect.contains(event.pos()):
                    current_state = index.data(Qt.CheckStateRole)
                    new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
                    model.setData(index, new_state, Qt.CheckStateRole)
                    return True
        return super().editorEvent(event, model, option, index)

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        widget = option.widget
        style = widget.style() if widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, widget)

        rect = option.rect
        is_selected = bool(option.state & QStyle.State_Selected)

        # 1. 繪製核取方塊
        check_state = index.data(Qt.CheckStateRole)
        x = rect.left() + 10
        if check_state is not None:
            check_opt = QStyleOptionViewItem(option)
            check_opt.rect = QRect(x, rect.top() + (rect.height() - 16) // 2, 16, 16)
            check_opt.state = option.state
            if check_state == Qt.Checked:
                check_opt.state |= QStyle.State_On
            else:
                check_opt.state = (check_opt.state & ~QStyle.State_On) | QStyle.State_Off
            style.drawPrimitive(QStyle.PE_IndicatorItemViewItemCheck, check_opt, painter, widget)
            x += 26

        orig_name = index.data(ORIG_NAME_ROLE) or os.path.basename(index.data(Qt.UserRole) or "")
        new_name = index.data(NEW_NAME_ROLE) or orig_name
        is_conflict = bool(index.data(IS_CONFLICT_ROLE))
        skip_prefix = bool(index.data(FLAG_SKIP_PREFIX))
        skip_strip = bool(index.data(FLAG_SKIP_STRIP))

        tags = []
        if skip_prefix:
            tags.append("略過前置")
        if skip_strip:
            tags.append("略過刪除")
        badge_text = ("  [" + ", ".join(tags) + "]") if tags else ""

        fm = painter.fontMetrics()
        adv = fm.horizontalAdvance if hasattr(fm, "horizontalAdvance") else fm.width

        badge_w = adv(badge_text) + 8 if badge_text else 0
        warning_w = adv("  ⚠️ 重複") + 8 if is_conflict else 0
        arrow_str = " ➔ "
        arrow_w = adv(arrow_str) + 12

        avail_w = rect.right() - x - badge_w - warning_w - arrow_w - 16
        col_w = max(50, avail_w // 2)

        y = rect.top() + (rect.height() + fm.ascent() - fm.descent()) // 2

        # 原始檔名
        elided_orig = fm.elidedText(orig_name, Qt.ElideMiddle, col_w)
        painter.setPen(QColor("#FFFFFF") if is_selected else QColor(TEXT_SEC))
        painter.drawText(x, y, elided_orig)

        # 箭頭符號
        arrow_x = x + col_w + 4
        painter.setPen(QColor("#FFFFFF") if is_selected else QColor(TEXT_DIM))
        painter.drawText(arrow_x, y, arrow_str)

        # 重新命名新檔名
        new_x = arrow_x + arrow_w
        elided_new = fm.elidedText(new_name, Qt.ElideMiddle, col_w)
        if is_conflict:
            col = QColor("#FF6B6B")
        elif is_selected:
            col = QColor("#FFFFFF")
        elif new_name != orig_name:
            col = QColor("#4EC9B0")
        else:
            col = QColor(TEXT_DIM)
        painter.setPen(col)
        painter.drawText(new_x, y, elided_new)

        # 衝突警告與標籤
        tail_x = new_x + col_w + 6
        if is_conflict:
            painter.setPen(QColor("#FF6B6B"))
            painter.drawText(tail_x, y, "⚠️ 重複")
            tail_x += warning_w
        if badge_text:
            painter.setPen(QColor("#FFFFFF") if is_selected else QColor(TEXT_DIM))
            painter.drawText(tail_x, y, badge_text)

        painter.restore()


class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setItemDelegate(RenameItemDelegate(self))

    def add_files(self, paths: list[str]) -> int:
        added_count = 0
        existing_paths = {self.item(i).data(Qt.UserRole) for i in range(self.count())}
        for file_path in paths:
            if not os.path.isfile(file_path):
                continue
            norm_path = os.path.abspath(file_path)
            if norm_path in existing_paths:
                continue
            existing_paths.add(norm_path)

            item = QListWidgetItem()
            item.setData(Qt.UserRole, norm_path)
            item.setData(ORIG_NAME_ROLE, os.path.basename(norm_path))
            item.setData(FLAG_SKIP_STRIP, False)
            item.setData(FLAG_SKIP_PREFIX, False)
            item.setData(NEW_NAME_ROLE, os.path.basename(norm_path))
            item.setData(IS_CONFLICT_ROLE, False)
            item.setSizeHint(QSize(0, 36))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self._refresh_item_text(item)
            self.addItem(item)
            added_count += 1
        return added_count

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
            file_paths = []
            for url in event.mimeData().urls():
                p = url.toLocalFile()
                if os.path.isfile(p):
                    file_paths.append(p)
                elif os.path.isdir(p):
                    # 遞迴掃描資料夾內的所有檔案，排除隱藏目錄與系統垃圾檔案
                    for root, dirs, files in os.walk(p):
                        dirs[:] = [d for d in dirs if not d.startswith(".")]
                        dirs.sort()
                        files.sort()
                        for f in files:
                            if f.startswith(".") or f.lower() in ("thumbs.db", "desktop.ini"):
                                continue
                            file_paths.append(os.path.join(root, f))
            if file_paths:
                self.add_files(file_paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.remove_selected()
        elif event.matches(QKeySequence.SelectAll):
            self.selectAll()
        else:
            super().keyPressEvent(event)

    def remove_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

    def sort_items(self, criterion: str):
        count = self.count()
        if count <= 1:
            return

        def natural_key(text: str):
            return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text)]

        def get_sort_key(item):
            fp = item.data(Qt.UserRole) or ""
            name = item.data(ORIG_NAME_ROLE) or os.path.basename(fp)
            if criterion in ("name_asc", "name_desc"):
                return natural_key(name)
            elif criterion in ("mtime_asc", "mtime_desc"):
                try:
                    return os.path.getmtime(fp) if os.path.exists(fp) else 0
                except Exception:
                    return 0
            elif criterion in ("size_asc", "size_desc"):
                try:
                    return os.path.getsize(fp) if os.path.exists(fp) else 0
                except Exception:
                    return 0
            elif criterion in ("ext_asc", "ext_desc"):
                ext = os.path.splitext(name)[1].lower()
                return (ext, natural_key(name))
            return natural_key(name)

        items = [self.takeItem(0) for _ in range(count)]
        reverse = criterion.endswith("_desc")
        items.sort(key=get_sort_key, reverse=reverse)

        self.blockSignals(True)
        for item in items:
            self.addItem(item)
        self.blockSignals(False)

    @staticmethod
    def _refresh_item_text(item):
        orig_name = item.data(ORIG_NAME_ROLE) or os.path.basename(item.data(Qt.UserRole) or "")
        new_name = item.data(NEW_NAME_ROLE) or orig_name
        is_conflict = item.data(IS_CONFLICT_ROLE)

        tags = []
        if item.data(FLAG_SKIP_PREFIX):
            tags.append("略過前置")
        if item.data(FLAG_SKIP_STRIP):
            tags.append("略過刪除")
        tag_str = f"  [{', '.join(tags)}]" if tags else ""

        if is_conflict:
            tag_str += " ⚠️ 重複衝突"

        item.setText(f"{orig_name}   ➔   {new_name}{tag_str}")

        fp = item.data(Qt.UserRole) or ""
        tooltip = f"原始路徑：{fp}"
        if new_name:
            target_dir = os.path.dirname(fp)
            tooltip += f"\n更名目標：{os.path.join(target_dir, new_name)}"
        if is_conflict:
            tooltip += "\n⚠️ 警告：此目標檔名在清單中有重複，請確認！"
        item.setToolTip(tooltip)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            return
        selected_items = self.selectedItems()
        if item not in selected_items:
            self.setCurrentItem(item)
            selected_items = [item]

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

        # 批次判斷選取項目前的狀態
        all_prefix_on = all(not (it.checkState() == Qt.Unchecked and it.data(FLAG_SKIP_PREFIX)) for it in selected_items)
        all_strip_on = all(not (it.checkState() == Qt.Unchecked and it.data(FLAG_SKIP_STRIP)) for it in selected_items)

        target_text = f"（共 {len(selected_items)} 個項目）" if len(selected_items) > 1 else ""

        act_prefix = QAction(f"套用前置詞 {target_text}".strip(), self)
        act_prefix.setCheckable(True)
        act_prefix.setChecked(all_prefix_on)
        act_prefix.triggered.connect(lambda checked: self._toggle_flags_batch(selected_items, FLAG_SKIP_PREFIX, checked))
        menu.addAction(act_prefix)

        act_strip = QAction(f"套用刪除前綴 {target_text}".strip(), self)
        act_strip.setCheckable(True)
        act_strip.setChecked(all_strip_on)
        act_strip.triggered.connect(lambda checked: self._toggle_flags_batch(selected_items, FLAG_SKIP_STRIP, checked))
        menu.addAction(act_strip)

        menu.addSeparator()

        act_remove = QAction(f"移除選取檔案 {target_text}".strip(), self)
        act_remove.triggered.connect(self.remove_selected)
        menu.addAction(act_remove)

        menu.exec_(event.globalPos())

    def _toggle_flags_batch(self, items, flag_role, enabled):
        for item in items:
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
