import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.operations import (
    RenameEntry,
    RenameResult,
    ConflictAction,
    build_rename_entries,
    build_undo_entries,
    generate_temp_path,
    execute_rename,
)


class TestBuildRenameEntries:
    def test_basic(self):
        entries = build_rename_entries(
            [r"C:\a.txt", r"C:\b.txt"],
            ["1a.txt", "2b.txt"],
        )
        assert len(entries) == 2
        assert entries[0].file_path == r"C:\a.txt"
        assert entries[0].new_name == "1a.txt"
        assert entries[1].file_path == r"C:\b.txt"
        assert entries[1].new_name == "2b.txt"

    def test_empty(self):
        entries = build_rename_entries([], [])
        assert len(entries) == 0


class TestGenerateTempPath:
    def test_temp_path(self):
        result = generate_temp_path(r"C:\dir\photo.jpg", "0")
        assert result == r"C:\dir\__rename_tmp_0.jpg"

    def test_temp_path_no_ext(self):
        result = generate_temp_path(r"C:\dir\file", "1")
        assert result == r"C:\dir\__rename_tmp_1"


class TestExecuteRename:
    def test_successful_rename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "old.txt")
            open(src, "w").close()
            entries = build_rename_entries([src], ["new.txt"])
            result = execute_rename(entries)

            assert len(result.successes) == 1
            assert result.successes[0] == (src, "new.txt")
            assert len(result.errors) == 0
            assert os.path.exists(os.path.join(tmpdir, "new.txt"))
            assert not os.path.exists(src)

    def test_file_not_found(self):
        entries = build_rename_entries(
            [r"C:\nonexistent\file.txt"], ["new.txt"]
        )
        result = execute_rename(entries)
        assert len(result.errors) == 1
        assert "不存在" in result.errors[0][2]

    def test_overwrite_skip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "old.txt")
            with open(src, "w") as f:
                f.write("original_content")
            existing = os.path.join(tmpdir, "existing.txt")
            with open(existing, "w") as f:
                f.write("existing_content")

            entries = build_rename_entries([src], ["existing.txt"])
            result = execute_rename(entries)

            assert len(result.skipped) == 1
            assert result.skipped[0] == (src, "existing.txt")
            assert os.path.exists(existing)
            assert os.path.exists(src)
            with open(src) as f:
                assert f.read() == "original_content"
            assert not os.path.exists(os.path.join(tmpdir, "_skipped_existing.txt"))

    def test_overwrite_confirm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "old.txt")
            open(src, "w").close()
            existing = os.path.join(tmpdir, "target.txt")
            open(existing, "w").close()

            handler = lambda p, n: ConflictAction.OVERWRITE
            entries = build_rename_entries([src], ["target.txt"])
            result = execute_rename(entries, conflict_handler=handler)

            assert len(result.successes) == 1
            assert os.path.exists(os.path.join(tmpdir, "target.txt"))
            assert not os.path.exists(src)
            with open(os.path.join(tmpdir, "target.txt")) as f:
                assert f.read() == ""

    def test_overwrite_cancel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src1 = os.path.join(tmpdir, "old1.txt")
            src2 = os.path.join(tmpdir, "old2.txt")
            open(src1, "w").close()
            open(src2, "w").close()
            existing = os.path.join(tmpdir, "target.txt")
            open(existing, "w").close()

            entry2 = os.path.join(tmpdir, "target2.txt")
            open(entry2, "w").close()

            handler = lambda p, n: ConflictAction.CANCEL
            entries = build_rename_entries([src1, src2], ["target.txt", "target2.txt"])

            result = execute_rename(entries, conflict_handler=handler)

            assert len(result.errors) == 0
            assert os.path.exists(src1)
            assert os.path.exists(src2)

    def test_cancel_after_partial_success_rolls_back_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src1 = os.path.join(tmpdir, "old1.txt")
            src2 = os.path.join(tmpdir, "old2.txt")
            with open(src1, "w") as f:
                f.write("content1")
            with open(src2, "w") as f:
                f.write("content2")

            existing = os.path.join(tmpdir, "target2.txt")
            open(existing, "w").close()

            # src1 -> new1.txt (no conflict), src2 -> target2.txt (conflicts)
            handler = lambda p, n: ConflictAction.CANCEL
            entries = build_rename_entries([src1, src2], ["new1.txt", "target2.txt"])

            result = execute_rename(entries, conflict_handler=handler)

            assert len(result.successes) == 0
            assert len(result.errors) == 0
            # Check both files were safely restored to original paths and contents
            assert os.path.exists(src1)
            assert not os.path.exists(os.path.join(tmpdir, "new1.txt"))
            with open(src1) as f:
                assert f.read() == "content1"

            assert os.path.exists(src2)
            with open(src2) as f:
                assert f.read() == "content2"

    def test_temp_path_avoids_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            colliding_temp = os.path.join(tmpdir, "__rename_tmp_0.txt")
            open(colliding_temp, "w").close()

            file_path = os.path.join(tmpdir, "file.txt")
            result = generate_temp_path(file_path, "0")

            assert result != colliding_temp
            assert not os.path.exists(result)

    def test_multiple_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = []
            for i in range(3):
                p = os.path.join(tmpdir, f"old_{i}.txt")
                open(p, "w").write(f"content_{i}")
                paths.append(p)

            new_names = [f"new_{i}.txt" for i in range(3)]
            entries = build_rename_entries(paths, new_names)
            result = execute_rename(entries)

            assert len(result.successes) == 3
            for i in range(3):
                assert os.path.exists(os.path.join(tmpdir, f"new_{i}.txt"))
                assert not os.path.exists(os.path.join(tmpdir, f"old_{i}.txt"))

    def test_progress_callback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "test.txt")
            open(src, "w").close()

            progress_records = []
            def on_progress(cur, total, msg):
                progress_records.append((cur, total, msg))

            entries = build_rename_entries([src], ["renamed.txt"])
            result = execute_rename(entries, progress_callback=on_progress)

            assert len(result.successes) == 1
            assert len(progress_records) > 0
            assert progress_records[-1][2] == "完成"


class TestUndoOperations:
    def test_build_undo_entries(self):
        successes = [
            (r"C:\docs\report.txt", "2024_report.txt"),
            (r"C:\photos\img.jpg", "pic_01.jpg"),
        ]
        undo_entries = build_undo_entries(successes)
        assert len(undo_entries) == 2
        assert undo_entries[0].file_path == os.path.join(r"C:\docs", "2024_report.txt")
        assert undo_entries[0].new_name == "report.txt"
        assert undo_entries[1].file_path == os.path.join(r"C:\photos", "pic_01.jpg")
        assert undo_entries[1].new_name == "img.jpg"

    def test_undo_restores_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = os.path.join(tmpdir, "doc1.txt")
            p2 = os.path.join(tmpdir, "doc2.txt")
            with open(p1, "w") as f:
                f.write("doc1_content")
            with open(p2, "w") as f:
                f.write("doc2_content")

            # 1. 執行重新命名
            entries = build_rename_entries([p1, p2], ["new_doc1.txt", "new_doc2.txt"])
            res1 = execute_rename(entries)
            assert len(res1.successes) == 2

            # 驗證新檔名存在，舊檔名不存在
            assert not os.path.exists(p1)
            assert not os.path.exists(p2)
            assert os.path.exists(os.path.join(tmpdir, "new_doc1.txt"))
            assert os.path.exists(os.path.join(tmpdir, "new_doc2.txt"))

            # 2. 執行 Undo 復原
            undo_entries = build_undo_entries(res1.successes)
            undo_res = execute_rename(undo_entries)
            assert len(undo_res.successes) == 2

            # 驗證檔案 100% 恢復回原本檔名與內容
            assert os.path.exists(p1)
            assert os.path.exists(p2)
            assert not os.path.exists(os.path.join(tmpdir, "new_doc1.txt"))
            assert not os.path.exists(os.path.join(tmpdir, "new_doc2.txt"))
            with open(p1) as f:
                assert f.read() == "doc1_content"
            with open(p2) as f:
                assert f.read() == "doc2_content"
