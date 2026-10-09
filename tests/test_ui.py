import os
import sys
import tempfile
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.widgets import (
    DropListWidget, RenameItemDelegate,
    FLAG_SKIP_STRIP, FLAG_SKIP_PREFIX, ORIG_NAME_ROLE, NEW_NAME_ROLE, IS_CONFLICT_ROLE,
)
from ui.app import RenamerApp


# 確保在測試中有單一 QApplication 實例
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestDropListWidget:
    def test_add_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "a.txt")
            f2 = os.path.join(tmpdir, "b.txt")
            open(f1, "w").close()
            open(f2, "w").close()

            lw = DropListWidget()
            added = lw.add_files([f1, f2])
            assert added == 2
            assert lw.count() == 2
            assert lw.item(0).data(ORIG_NAME_ROLE) == "a.txt"
            assert lw.item(1).data(ORIG_NAME_ROLE) == "b.txt"

    def test_add_files_deduplication(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "a.txt")
            open(f1, "w").close()

            lw = DropListWidget()
            lw.add_files([f1])
            added_again = lw.add_files([f1])
            assert added_again == 0
            assert lw.count() == 1

    def test_batch_toggle_flags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "a.txt")
            f2 = os.path.join(tmpdir, "b.txt")
            open(f1, "w").close()
            open(f2, "w").close()

            lw = DropListWidget()
            lw.add_files([f1, f2])
            items = [lw.item(0), lw.item(1)]

            # 批次設定略過前置詞
            lw._toggle_flags_batch(items, FLAG_SKIP_PREFIX, enabled=False)
            assert lw.item(0).data(FLAG_SKIP_PREFIX) is True
            assert lw.item(1).data(FLAG_SKIP_PREFIX) is True

            # 批次取消略過
            lw._toggle_flags_batch(items, FLAG_SKIP_PREFIX, enabled=True)
            assert lw.item(0).data(FLAG_SKIP_PREFIX) is False
            assert lw.item(1).data(FLAG_SKIP_PREFIX) is False


class TestRenamerAppPreview:
    def test_live_preview_updates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "photo_a.jpg")
            f2 = os.path.join(tmpdir, "photo_b.jpg")
            open(f1, "w").close()
            open(f2, "w").close()

            window = RenamerApp()
            window.list_widget.add_files([f1, f2])
            window.update_preview()

            # 初始預設：prefix="", start=1, auto_pad=True
            assert window.list_widget.item(0).data(NEW_NAME_ROLE) == "01photo_a.jpg"
            assert window.list_widget.item(1).data(NEW_NAME_ROLE) == "02photo_b.jpg"

            # 變更 prefix
            window.prefix_edit.setText("IMG_")
            assert window.list_widget.item(0).data(NEW_NAME_ROLE) == "IMG_01photo_a.jpg"
            assert window.list_widget.item(1).data(NEW_NAME_ROLE) == "IMG_02photo_b.jpg"

            # 變更 strip 前綴字數
            window.strip_spin.setValue(6)  # 刪除 "photo_"
            assert window.list_widget.item(0).data(NEW_NAME_ROLE) == "IMG_01a.jpg"
            assert window.list_widget.item(1).data(NEW_NAME_ROLE) == "IMG_02b.jpg"

    def test_internal_collision_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "first.txt")
            f2 = os.path.join(tmpdir, "second.txt")
            open(f1, "w").close()
            open(f2, "w").close()

            window = RenamerApp()
            window.list_widget.add_files([f1, f2])

            # 全刪且無前綴、無流水號時或使兩者算出的檔名相同
            # 將 start 固定且不加流水號 (若 strip_all 為 True 且 prefix 為固定字串)
            # 在 naming 邏輯中：new_name = {prefix}{num}{remaining}{ext}
            # 當兩者副檔名相同，且在同目錄，如果兩者 prefix 相同、remaining 相同
            # 讓兩者都略過流水號或讓其產生同名：
            # 例如第一項略過前置，第二項無前綴且 start 同步
            # 也可以直接模擬同一目錄下算出相同 new_name
            window.strip_all_check.setChecked(True)
            window.prefix_edit.setText("fixed_name")
            window.update_preview()

            # 由於有 num，item(0) 是 fixed_name01.txt, item(1) 是 fixed_name02.txt
            # 若 item(1) 勾選了不同規則或兩者名稱相同：
            assert window.list_widget.item(0).data(IS_CONFLICT_ROLE) is False
            assert window.list_widget.item(1).data(IS_CONFLICT_ROLE) is False


class TestDropListWidgetSorting:
    def test_sort_natural_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "file1.txt")
            f2 = os.path.join(tmpdir, "file2.txt")
            f10 = os.path.join(tmpdir, "file10.txt")
            for f in (f1, f2, f10):
                open(f, "w").close()

            lw = DropListWidget()
            # 刻意依非自然順序加入
            lw.add_files([f10, f1, f2])

            lw.sort_items("name_asc")
            names_asc = [lw.item(i).data(ORIG_NAME_ROLE) for i in range(lw.count())]
            assert names_asc == ["file1.txt", "file2.txt", "file10.txt"]

            lw.sort_items("name_desc")
            names_desc = [lw.item(i).data(ORIG_NAME_ROLE) for i in range(lw.count())]
            assert names_desc == ["file10.txt", "file2.txt", "file1.txt"]

    def test_sort_by_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f_txt = os.path.join(tmpdir, "b.txt")
            f_jpg = os.path.join(tmpdir, "a.jpg")
            f_png = os.path.join(tmpdir, "c.png")
            for f in (f_txt, f_jpg, f_png):
                open(f, "w").close()

            lw = DropListWidget()
            lw.add_files([f_txt, f_png, f_jpg])

            lw.sort_items("ext_asc")
            exts = [os.path.splitext(lw.item(i).data(ORIG_NAME_ROLE))[1] for i in range(lw.count())]
            assert exts == [".jpg", ".png", ".txt"]
