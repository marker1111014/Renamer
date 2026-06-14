import os


def compute_new_name(
    file_path: str,
    index: int,
    total_count: int,
    strip: int = 0,
    prefix: str = "",
    start: int = 1,
    auto_pad: bool = True,
    skip_strip: bool = False,
    skip_prefix: bool = False,
    strip_all: bool = False,
) -> tuple[str, str]:
    name, ext = os.path.splitext(os.path.basename(file_path))
    if skip_strip:
        remaining = name
    elif strip_all:
        remaining = ""
    else:
        remaining = name[strip:] if strip < len(name) else ""
    raw_width = len(str(start + total_count - 1)) if total_count else 1
    pad_width = max(2, raw_width) if auto_pad else 0
    num = f"{start + index:0{pad_width}d}" if pad_width else str(start + index)
    new_name = f"{'' if skip_prefix else prefix}{num}{remaining}{ext}"
    new_path = os.path.join(os.path.dirname(file_path), new_name)
    return new_name, new_path


def compute_pad_width(total_count: int, start: int, auto_pad: bool) -> int:
    if not auto_pad:
        return 0
    raw = len(str(start + total_count - 1)) if total_count else 1
    return max(2, raw)
