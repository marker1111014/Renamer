import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


class ConflictAction(Enum):
    OVERWRITE = auto()
    SKIP = auto()
    CANCEL = auto()


@dataclass
class RenameEntry:
    file_path: str
    new_name: str
    temp_path: str = ""


@dataclass
class RenameResult:
    successes: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    errors: list[tuple[str, str, str]] = field(default_factory=list)


def build_rename_entries(
    file_paths: list[str],
    new_names: list[str],
) -> list[RenameEntry]:
    entries = []
    for file_path, new_name in zip(file_paths, new_names):
        entries.append(RenameEntry(file_path=file_path, new_name=new_name))
    return entries


def generate_temp_path(file_path: str, tag: str = "") -> str:
    dir_name = os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1]
    temp_name = f"__rename_tmp_{tag}{ext}"
    return os.path.join(dir_name, temp_name)


def execute_rename(
    entries: list[RenameEntry],
    conflict_handler: Callable[[str, str], ConflictAction] | None = None,
) -> RenameResult:
    result = RenameResult()
    temp_entries: list[tuple[str, RenameEntry]] = []

    for i, entry in enumerate(entries):
        file_path = entry.file_path
        if not os.path.exists(file_path):
            result.errors.append((file_path, entry.new_name, "原始檔案不存在"))
            continue

        tag = str(i)
        temp_path = generate_temp_path(file_path, tag)
        try:
            os.rename(file_path, temp_path)
        except Exception as e:
            result.errors.append((file_path, entry.new_name, f"暫存失敗: {e}"))
            _rollback_temp(temp_entries)
            return result
        temp_entries.append((temp_path, entry))
        entry.temp_path = temp_path

    for temp_path, entry in temp_entries:
        new_path = os.path.join(os.path.dirname(entry.file_path), entry.new_name)
        final_name = entry.new_name

        if os.path.exists(new_path):
            if conflict_handler:
                action = conflict_handler(new_path, final_name)
            else:
                action = ConflictAction.SKIP

            if action == ConflictAction.CANCEL:
                _rollback_temp(temp_entries)
                return result
            elif action == ConflictAction.SKIP:
                skipped_name = f"_skipped_{final_name}"
                skipped_path = os.path.join(os.path.dirname(new_path), skipped_name)
                try:
                    os.rename(temp_path, skipped_path)
                except Exception:
                    os.rename(temp_path, new_path)
                    result.successes.append((entry.file_path, final_name))
                    continue
                result.skipped.append((entry.file_path, final_name))
                continue
            elif action == ConflictAction.OVERWRITE:
                try:
                    os.remove(new_path)
                except Exception as e:
                    result.errors.append((entry.file_path, final_name, f"無法覆蓋: {e}"))
                    _rollback_temp(temp_entries)
                    return result

        try:
            os.rename(temp_path, new_path)
            result.successes.append((entry.file_path, final_name))
        except Exception as e:
            result.errors.append((entry.file_path, final_name, f"重新命名失敗: {e}"))
            _rollback_temp(temp_entries)
            return result

    return result


def _rollback_temp(temp_entries: list[tuple[str, RenameEntry]]) -> None:
    for temp_path, entry in temp_entries:
        if os.path.exists(temp_path):
            original = entry.file_path
            if not os.path.exists(original):
                try:
                    os.rename(temp_path, original)
                except Exception:
                    pass
