import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSpinBox, QLabel, QMessageBox,
    QLineEdit, QCheckBox, QFrame, QFileDialog,
    QProgressBar, QMenu, QAction, QShortcut,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QKeySequence

from core.naming import compute_new_name
from core.operations import build_rename_entries, build_undo_entries, execute_rename, ConflictAction
from ui.theme import (
    BG_DEEP, BG_CARD, BG_HOVER, TEXT, TEXT_SEC, TEXT_DIM, BORDER,
    S_BASE, S_LIST, S_LIST_HEADER, S_BTN_FLAT, S_BTN_PRIMARY, S_INPUT, S_CHECKBOX,
    S_HEADER, S_STATUS, S_PROGRESS_BAR,
)
from ui.widgets import (
    DropListWidget, FLAG_SKIP_STRIP, FLAG_SKIP_PREFIX,
    ORIG_NAME_ROLE, NEW_NAME_ROLE, IS_CONFLICT_ROLE,
)
from ui.worker import RenameWorker
from ui.preview import PreviewDialog


class RenamerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("重新命名工具")
        self.setGeometry(100, 100, 800, 620)
        self.setMinimumSize(640, 480)

        self.undo_stack: list[list[tuple[str, str]]] = []
        self.current_worker: RenameWorker | None = None
        self._active_item_map: dict[str, any] = {}
        self._is_undo_operation: bool = False

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
        h.setContentsMargins(28, 20, 28, 16)
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

        d = QLabel("點擊按鈕或直接拖曳檔案／資料夾至清單，即時預覽更名效果，右鍵可設定個別規則")
        d.setStyleSheet(S_HEADER)
        h.addWidget(d)
        root.addWidget(header)

        # ── Content ───────────────────────────────────────────
        c = QVBoxLayout()
        c.setContentsMargins(28, 16, 28, 16)
        c.setSpacing(12)

        # ── Action Toolbar (新增檔案 / 資料夾 / 排序 / 復原 / 移除 / 清空) ───
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_add_files = QPushButton("＋ 加入檔案")
        self.btn_add_files.setStyleSheet(S_BTN_FLAT)
        self.btn_add_files.setCursor(Qt.PointingHandCursor)
        self.btn_add_files.clicked.connect(self.add_files_dialog)
        toolbar.addWidget(self.btn_add_files)

        self.btn_add_dir = QPushButton("📁 加入資料夾")
        self.btn_add_dir.setStyleSheet(S_BTN_FLAT)
        self.btn_add_dir.setCursor(Qt.PointingHandCursor)
        self.btn_add_dir.clicked.connect(self.add_directory_dialog)
        toolbar.addWidget(self.btn_add_dir)

        self.btn_sort = QPushButton("⇅ 排序 ▾")
        self.btn_sort.setStyleSheet(S_BTN_FLAT)
        self.btn_sort.setCursor(Qt.PointingHandCursor)
        self._setup_sort_menu()
        toolbar.addWidget(self.btn_sort)

        self.btn_undo = QPushButton("↶ 復原")
        self.btn_undo.setStyleSheet(S_BTN_FLAT)
        self.btn_undo.setCursor(Qt.PointingHandCursor)
        self.btn_undo.setEnabled(False)
        self.btn_undo.setToolTip("復原上次重新命名的檔案 (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo_last_rename)
        toolbar.addWidget(self.btn_undo)

        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_last_rename)

        toolbar.addSpacing(6)

        self.btn_remove = QPushButton("移除選取")
        self.btn_remove.setStyleSheet(S_BTN_FLAT)
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.clicked.connect(self.remove_selected)
        toolbar.addWidget(self.btn_remove)

        self.btn_clear = QPushButton("清空列表")
        self.btn_clear.setStyleSheet(S_BTN_FLAT)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_list)
        toolbar.addWidget(self.btn_clear)

        toolbar.addStretch()

        self.count_badge = QLabel("0 個檔案")
        self.count_badge.setStyleSheet(f"font-size: 13px; color: {TEXT_SEC};")
        toolbar.addWidget(self.count_badge)

        c.addLayout(toolbar)

        # ── List Column Header Bar ────────────────────────────
        list_header = QFrame()
        list_header.setObjectName("listHeader")
        list_header.setStyleSheet(S_LIST_HEADER)
        lh = QHBoxLayout(list_header)
        lh.setContentsMargins(14, 6, 14, 6)
        lh.setSpacing(8)

        lh_orig = QLabel("原始檔案名稱")
        lh_orig.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_SEC};")
        lh.addWidget(lh_orig)

        lh_arrow = QLabel("➔")
        lh_arrow.setStyleSheet(f"font-size: 13px; color: {TEXT_DIM};")
        lh.addWidget(lh_arrow)

        lh_new = QLabel("重新命名即時預覽")
        lh_new.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_SEC};")
        lh.addWidget(lh_new)

        lh.addStretch()

        lh_status = QLabel("個別規則與狀態")
        lh_status.setStyleSheet(f"font-size: 12px; color: {TEXT_DIM};")
        lh.addWidget(lh_status)

        c.addWidget(list_header)

        # ── List Widget ───────────────────────────────────────
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
        self.prefix_edit.setMaximumWidth(140)
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

        self.btn_rename = QPushButton("開始重新命名")
        self.btn_rename.setStyleSheet(S_BTN_PRIMARY)
        self.btn_rename.setCursor(Qt.PointingHandCursor)
        self.btn_rename.clicked.connect(self.rename_files)
        row2.addWidget(self.btn_rename)

        opt_container.addLayout(row2)
        c.addLayout(opt_container)

        root.addLayout(c)

        # ── Progress Bar ──────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(S_PROGRESS_BAR)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)

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

        self.status_label = QLabel("尚未加入任何檔案 — 可點擊上方按鈕或從檔案總管拖曳檔案／資料夾")
        self.status_label.setStyleSheet(S_STATUS)
        sbl.addWidget(self.status_label)

        sbl.addStretch()
        root.addWidget(sb)

        # ── Signals for Real-time Live Preview ────────────────
        self.strip_spin.valueChanged.connect(self.update_preview)
        self.strip_all_check.toggled.connect(self.update_preview)
        self.prefix_edit.textChanged.connect(self.update_preview)
        self.start_spin.valueChanged.connect(self.update_preview)
        self.auto_pad_check.toggled.connect(self.update_preview)

        self.list_widget.model().rowsInserted.connect(self.update_preview)
        self.list_widget.model().rowsRemoved.connect(self.update_preview)
        self.list_widget.model().rowsMoved.connect(self.update_preview)
        self.list_widget.itemChanged.connect(self._on_item_changed)

    def _setup_sort_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
                color: {TEXT};
            }}
            QMenu::item {{
                padding: 6px 20px 6px 10px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: {BG_HOVER};
                color: {TEXT};
            }}
        """)

        sort_options = [
            ("🔤 檔名正序 (A ➔ Z)", "name_asc"),
            ("🔤 檔名倒序 (Z ➔ A)", "name_desc"),
            ("🕒 修改時間 (舊 ➔ 新)", "mtime_asc"),
            ("🕒 修改時間 (新 ➔ 舊)", "mtime_desc"),
            ("📄 檔案大小 (小 ➔ 大)", "size_asc"),
            ("📄 檔案大小 (大 ➔ 小)", "size_desc"),
            ("🏷️ 依照副檔名類型", "ext_asc"),
        ]
        for title, criterion in sort_options:
            act = QAction(title, self)
            act.triggered.connect(lambda _, c=criterion: self._sort_files(c))
            menu.addAction(act)

        self.btn_sort.setMenu(menu)

    def _sort_files(self, criterion: str):
        self.list_widget.sort_items(criterion)
        self.update_preview()

    def set_controls_enabled(self, enabled: bool):
        self.btn_rename.setEnabled(enabled)
        self.btn_add_files.setEnabled(enabled)
        self.btn_add_dir.setEnabled(enabled)
        self.btn_sort.setEnabled(enabled)
        self.btn_undo.setEnabled(enabled and len(self.undo_stack) > 0)
        self.btn_clear.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.strip_spin.setEnabled(enabled and not self.strip_all_check.isChecked())
        self.strip_all_check.setEnabled(enabled)
        self.prefix_edit.setEnabled(enabled)
        self.start_spin.setEnabled(enabled)
        self.auto_pad_check.setEnabled(enabled)
        self.list_widget.setEnabled(enabled)

    def add_files_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "選擇要重新命名的檔案",
            "",
            "所有檔案 (*.*)",
        )
        if paths:
            self.list_widget.add_files(paths)
            self.update_preview()

    def add_directory_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "選擇要加入的資料夾",
            "",
            QFileDialog.ShowDirsOnly,
        )
        if dir_path:
            paths = []
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                dirs.sort()
                files.sort()
                for f in files:
                    if f.startswith(".") or f.lower() in ("thumbs.db", "desktop.ini"):
                        continue
                    paths.append(os.path.join(root, f))
            if paths:
                self.list_widget.add_files(paths)
                self.update_preview()

    def update_preview(self):
        count = self.list_widget.count()
        self.count_badge.setText(f"{count} 個檔案")

        if count == 0:
            self.status_label.setText("尚未加入任何檔案 — 可點擊上方按鈕或從檔案總管拖曳檔案／資料夾")
            return

        strip = self.strip_spin.value()
        prefix_val = self.prefix_edit.text().strip()
        start = self.start_spin.value()
        auto_pad = self.auto_pad_check.isChecked()
        strip_all = self.strip_all_check.isChecked()

        # 1. 批次計算每個檔案的新名稱
        computed_names = []
        for i in range(count):
            item = self.list_widget.item(i)
            fp = item.data(Qt.UserRole)
            if not fp:
                computed_names.append("")
                continue

            skip_strip = (item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_STRIP))
            skip_prefix = (item.checkState() == Qt.Unchecked and item.data(FLAG_SKIP_PREFIX))

            new_name, _ = compute_new_name(
                fp, i, count,
                strip=strip, prefix=prefix_val, start=start, auto_pad=auto_pad,
                skip_strip=skip_strip, skip_prefix=skip_prefix,
                strip_all=strip_all,
            )
            computed_names.append(new_name)

        # 2. 檢測批次內的目標路徑衝突 (同目錄下重複新名稱)
        target_counts = {}
        for i in range(count):
            item = self.list_widget.item(i)
            fp = item.data(Qt.UserRole)
            if not fp:
                continue
            dir_name = os.path.dirname(fp)
            key = os.path.normcase(os.path.join(dir_name, computed_names[i]))
            target_counts[key] = target_counts.get(key, 0) + 1

        conflict_count = 0
        changed_count = 0

        # 3. 更新各項目 Role 與顯示
        self.list_widget.blockSignals(True)
        for i in range(count):
            item = self.list_widget.item(i)
            fp = item.data(Qt.UserRole)
            if not fp:
                continue
            orig_name = item.data(ORIG_NAME_ROLE) or os.path.basename(fp)
            new_name = computed_names[i]

            dir_name = os.path.dirname(fp)
            key = os.path.normcase(os.path.join(dir_name, new_name))
            is_conflict = target_counts.get(key, 0) > 1

            if is_conflict:
                conflict_count += 1
            if new_name != orig_name:
                changed_count += 1

            item.setData(NEW_NAME_ROLE, new_name)
            item.setData(IS_CONFLICT_ROLE, is_conflict)
            DropListWidget._refresh_item_text(item)

        self.list_widget.blockSignals(False)
        self.list_widget.viewport().update()

        # 4. 更新狀態列文字
        n_strip = sum(1 for i in range(count)
                      if self.list_widget.item(i).checkState() == Qt.Unchecked
                      and self.list_widget.item(i).data(FLAG_SKIP_STRIP))
        n_prefix = sum(1 for i in range(count)
                       if self.list_widget.item(i).checkState() == Qt.Unchecked
                       and self.list_widget.item(i).data(FLAG_SKIP_PREFIX))

        parts = [f"已加入 {count} 個檔案"]
        if changed_count > 0:
            parts.append(f"{changed_count} 個將被變更")
        if n_strip:
            parts.append(f"{n_strip} 個不刪除前綴")
        if n_prefix:
            parts.append(f"{n_prefix} 個不加前置詞")

        if conflict_count > 0:
            parts.append(f"⚠️ 偵測到 {conflict_count} 個新檔名重複衝突！")
        else:
            parts.append("確認順序無誤後點擊「開始重新命名」")

        self.status_label.setText("  |  ".join(parts))

    def _on_strip_all_toggled(self, checked):
        self.strip_spin.setEnabled(not checked)
        self.update_preview()

    def _on_item_changed(self, item):
        item.setForeground(QColor(TEXT) if item.checkState() == Qt.Checked else QColor(TEXT_SEC))
        DropListWidget._refresh_item_text(item)
        self.update_preview()

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))
        self.update_preview()

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
            self.update_preview()

    def rename_files(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, "警告", "請先加入要重新命名的檔案")
            return

        total = self.list_widget.count()
        file_paths = []
        new_names = []
        item_map = {}
        has_internal_conflict = False

        for i in range(total):
            item = self.list_widget.item(i)
            fp = item.data(Qt.UserRole)
            if not fp or not os.path.exists(fp):
                continue

            if item.data(IS_CONFLICT_ROLE):
                has_internal_conflict = True

            nn = item.data(NEW_NAME_ROLE) or os.path.basename(fp)
            file_paths.append(fp)
            new_names.append(nn)
            item_map[fp] = item

        if not file_paths:
            QMessageBox.warning(self, "警告", "沒有有效的檔案可供重新命名")
            return

        if has_internal_conflict:
            warn_reply = QMessageBox.warning(
                self, "目標檔名衝突警告",
                "清單中存在重複的目標檔名，若繼續執行可能導致檔案相互覆蓋或操作失敗！\n\n建議先調整前綴、起始數字或刪除字數。\n是否仍要開啟預覽並繼續？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if warn_reply != QMessageBox.Yes:
                return

        preview_data = [(os.path.basename(fp), nn) for fp, nn in zip(file_paths, new_names)]
        dialog = PreviewDialog(preview_data, self)
        if not dialog.exec_():
            return

        entries = build_rename_entries(file_paths, new_names)
        self._active_item_map = item_map
        self._is_undo_operation = False
        self._start_worker(entries)

    def undo_last_rename(self):
        if not self.undo_stack:
            return

        last_successes = self.undo_stack[-1]
        reply = QMessageBox.question(
            self, "確認復原",
            f"即將還原上次重新命名的 {len(last_successes)} 個檔案名稱，是否確定執行？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.undo_stack.pop()
        undo_entries = build_undo_entries(last_successes)
        self._is_undo_operation = True
        self._start_worker(undo_entries)

    def _start_worker(self, entries):
        self.set_controls_enabled(False)
        total_steps = len(entries) * 2 if entries else 1
        self.progress_bar.setMaximum(total_steps)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("處理中... %p%")
        self.progress_bar.setVisible(True)

        self.current_worker = RenameWorker(entries, self)
        self.current_worker.progress.connect(self._on_worker_progress)
        self.current_worker.conflict_needed.connect(self._on_worker_conflict_needed)
        self.current_worker.finished_signal.connect(self._on_worker_finished)
        self.current_worker.start()

    def _on_worker_progress(self, current, total, msg):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(msg)

    def _on_worker_conflict_needed(self, new_path, new_name):
        action = self._handle_conflict(new_path, new_name)
        if self.current_worker:
            self.current_worker.resolve_conflict(action)

    def _on_worker_finished(self, result):
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)

        if not self._is_undo_operation:
            if result.successes:
                self.undo_stack.append(result.successes)
                self.btn_undo.setEnabled(True)

            for orig_path, actual_new_name in result.successes:
                item = self._active_item_map.get(orig_path)
                if item is not None:
                    new_full_path = os.path.join(os.path.dirname(orig_path), actual_new_name)
                    item.setData(Qt.UserRole, new_full_path)
                    item.setData(ORIG_NAME_ROLE, actual_new_name)
                    item.setData(NEW_NAME_ROLE, actual_new_name)

            self.update_preview()

            msg_parts = [f"成功重新命名 {len(result.successes)} 個檔案"]
            if result.skipped:
                msg_parts.append(f"{len(result.skipped)} 個跳過")
            if result.errors:
                msg_parts.append(f"{len(result.errors)} 個失敗")
            QMessageBox.information(self, "完成", "，".join(msg_parts))
        else:
            # 復原完成
            for current_full_path, original_name in result.successes:
                dir_name = os.path.dirname(current_full_path)
                restored_path = os.path.join(dir_name, original_name)
                # 更新清單內對應的 item
                for i in range(self.list_widget.count()):
                    it = self.list_widget.item(i)
                    if it.data(Qt.UserRole) == current_full_path:
                        it.setData(Qt.UserRole, restored_path)
                        it.setData(ORIG_NAME_ROLE, original_name)
                        it.setData(NEW_NAME_ROLE, original_name)
                        break

            self.btn_undo.setEnabled(len(self.undo_stack) > 0)
            self.update_preview()
            QMessageBox.information(self, "復原完成", f"已成功還原 {len(result.successes)} 個檔案名稱！")

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
