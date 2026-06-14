import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.naming import compute_new_name, compute_pad_width


class TestComputePadWidth:
    def test_auto_pad_single_digit(self):
        assert compute_pad_width(1, 1, True) == 2

    def test_auto_pad_two_digits(self):
        assert compute_pad_width(100, 1, True) == 3

    def test_auto_pad_custom_start(self):
        assert compute_pad_width(10, 95, True) == 3

    def test_auto_pad_off(self):
        assert compute_pad_width(100, 1, False) == 0

    def test_zero_count(self):
        assert compute_pad_width(0, 1, True) == 2


class TestComputeNewName:
    def test_basic_numbering(self):
        new_name, new_path = compute_new_name(
            r"C:\test\photo.jpg", 0, 3, strip=0, prefix="", start=1, auto_pad=True
        )
        assert new_name == "01photo.jpg"

    def test_with_prefix(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 0, 3, strip=0, prefix="IMG_", start=1, auto_pad=True
        )
        assert new_name == "IMG_01photo.jpg"

    def test_strip_prefix_chars(self):
        new_name, _ = compute_new_name(
            r"C:\test\IMG_photo.jpg", 0, 3, strip=4, prefix="", start=1, auto_pad=True
        )
        assert new_name == "01photo.jpg"

    def test_strip_and_prefix(self):
        new_name, _ = compute_new_name(
            r"C:\test\IMG_photo.jpg", 1, 3, strip=4, prefix="NEW_", start=1, auto_pad=True
        )
        assert new_name == "NEW_02photo.jpg"

    def test_skip_strip(self):
        new_name, _ = compute_new_name(
            r"C:\test\IMG_photo.jpg", 0, 1, strip=4, prefix="", start=1,
            auto_pad=True, skip_strip=True
        )
        assert new_name == "01IMG_photo.jpg"

    def test_skip_prefix(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 0, 1, strip=0, prefix="PREFIX_", start=1,
            auto_pad=True, skip_prefix=True
        )
        assert new_name == "01photo.jpg"

    def test_no_auto_pad(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 0, 3, strip=0, prefix="", start=1, auto_pad=False
        )
        assert new_name == "1photo.jpg"

    def test_custom_start_number(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 2, 5, strip=0, prefix="", start=100, auto_pad=True
        )
        assert new_name == "102photo.jpg"

    def test_new_path_correct(self):
        _, new_path = compute_new_name(
            r"C:\test\sub\photo.jpg", 0, 1, strip=0, prefix="", start=1
        )
        assert new_path == os.path.join(r"C:\test\sub", "01photo.jpg")

    def test_extension_preserved(self):
        new_name, _ = compute_new_name(
            r"C:\test\file.txt", 0, 1, strip=2, prefix="log_", start=1
        )
        assert new_name == "log_01le.txt"

    def test_strip_greater_than_length(self):
        new_name, _ = compute_new_name(
            r"C:\test\ab.jpg", 0, 1, strip=10, prefix="", start=1, auto_pad=True
        )
        assert new_name == "01.jpg"

    def test_empty_prefix_when_skipped(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 0, 1, strip=0, prefix="", start=1,
            auto_pad=False, skip_prefix=False
        )
        assert new_name == "1photo.jpg"

    def test_multi_digit_numbering(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 99, 100, strip=0, prefix="", start=1, auto_pad=True
        )
        assert new_name == "100photo.jpg"

    def test_various_extensions(self):
        for ext in [".tar.gz", ".py", ".JPG", ".txt"]:
            new_name, _ = compute_new_name(
                rf"C:\test\file{ext}", 0, 1, strip=0, prefix="", start=1, auto_pad=False
            )
            assert new_name.endswith(ext), f"Failed for extension {ext}"

    def test_unicode_filename(self):
        new_name, _ = compute_new_name(
            r"C:\test\中文文件.txt", 0, 1, strip=0, prefix="", start=1, auto_pad=False
        )
        assert new_name == "1中文文件.txt"

    def test_strip_all(self):
        new_name, _ = compute_new_name(
            r"C:\test\IMG_photo.jpg", 0, 3, strip=0, prefix="", start=1,
            auto_pad=True, strip_all=True
        )
        assert new_name == "01.jpg"

    def test_strip_all_with_prefix(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 1, 3, strip=0, prefix="IMG_", start=1,
            auto_pad=True, strip_all=True
        )
        assert new_name == "IMG_02.jpg"

    def test_strip_all_ignores_strip_value(self):
        new_name, _ = compute_new_name(
            r"C:\test\abcdef.jpg", 0, 1, strip=3, prefix="", start=1,
            auto_pad=False, strip_all=True
        )
        assert new_name == "1.jpg"

    def test_skip_strip_overrides_strip_all(self):
        new_name, _ = compute_new_name(
            r"C:\test\photo.jpg", 0, 1, strip=0, prefix="", start=1,
            auto_pad=False, skip_strip=True, strip_all=True
        )
        assert new_name == "1photo.jpg"
