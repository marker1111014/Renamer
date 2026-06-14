import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.operations import (
    RenameEntry,
    RenameResult,
    ConflictAction,
    build_rename_entries,
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
            open(src, "w").close()
            existing = os.path.join(tmpdir, "existing.txt")
            open(existing, "w").close()

            entries = build_rename_entries([src], ["existing.txt"])
            result = execute_rename(entries)

            assert len(result.skipped) == 1
            assert result.skipped[0] == (src, "existing.txt")
            assert os.path.exists(existing)
            assert not os.path.exists(src)

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
