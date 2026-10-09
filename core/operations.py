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


def build_undo_entries(successes: list[tuple[str, str]]) -> list[RenameEntry]:
    """
    依據先前 execute_rename 的 successes 清單 [(original_path, new_name), ...]，
    建立反向復原所需的 RenameEntry 清單。
    """
    entries = []
    for orig_path, new_name in successes:
        dir_name = os.path.dirname(orig_path)
        current_full_path = os.path.join(dir_name, new_name)
        orig_name = os.path.basename(orig_path)
        entries.append(RenameEntry(file_path=current_full_path, new_name=orig_name))
    return entries


def generate_temp_path(file_path: str, tag: str = "") -> str:
    dir_name = os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1]
    temp_name = f"__rename_tmp_{tag}{ext}"
    candidate = os.path.join(dir_name, temp_name)
    if not os.path.exists(candidate):
        return candidate
    counter = 1
    while True:
        alt_name = f"__rename_tmp_{tag}_{counter}{ext}"
        candidate = os.path.join(dir_name, alt_name)
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def execute_rename(
    entries: list[RenameEntry],
    conflict_handler: Callable[[str, str], ConflictAction] | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> RenameResult:
    result = RenameResult()
    phase1_moved: list[RenameEntry] = []
    phase2_succeeded: list[tuple[RenameEntry, str]] = []
    phase2_skipped: set[str] = set()

    total_steps = len(entries) * 2 if entries else 1

    # 第一階段：將所有檔案移動至唯一的暫存檔名
    for i, entry in enumerate(entries):
        file_path = entry.file_path
        if progress_callback:
            progress_callback(i, total_steps, f"準備暫存: {os.path.basename(file_path)}")

        if not os.path.exists(file_path):
            result.errors.append((file_path, entry.new_name, "原始檔案不存在"))
            continue

        tag = str(i)
        temp_path = generate_temp_path(file_path, tag)
        try:
            os.rename(file_path, temp_path)
        except Exception as e:
            result.errors.append((file_path, entry.new_name, f"暫存失敗: {e}"))
            _rollback_all(phase1_moved, phase2_succeeded, phase2_skipped)
            return result
        entry.temp_path = temp_path
        phase1_moved.append(entry)

    # 第二階段：由暫存檔名移動至最終的新檔名
    for idx, entry in enumerate(phase1_moved):
        step = len(entries) + idx
        temp_path = entry.temp_path
        new_path = os.path.join(os.path.dirname(entry.file_path), entry.new_name)
        final_name = entry.new_name

        if progress_callback:
            progress_callback(step, total_steps, f"正在重新命名: {final_name}")

        if os.path.exists(new_path):
            if conflict_handler:
                action = conflict_handler(new_path, final_name)
            else:
                action = ConflictAction.SKIP

            if action == ConflictAction.CANCEL:
                _rollback_all(phase1_moved, phase2_succeeded, phase2_skipped)
                result.successes.clear()
                result.skipped.clear()
                return result
            elif action == ConflictAction.SKIP:
                try:
                    os.rename(temp_path, entry.file_path)
                except Exception as e:
                    result.errors.append((entry.file_path, final_name, f"略過還原失敗: {e}"))
                    _rollback_all(phase1_moved, phase2_succeeded, phase2_skipped)
                    result.successes.clear()
                    result.skipped.clear()
                    return result
                result.skipped.append((entry.file_path, final_name))
                phase2_skipped.add(entry.file_path)
                continue
            elif action == ConflictAction.OVERWRITE:
                try:
                    os.remove(new_path)
                except Exception as e:
                    result.errors.append((entry.file_path, final_name, f"無法覆蓋: {e}"))
                    _rollback_all(phase1_moved, phase2_succeeded, phase2_skipped)
                    result.successes.clear()
                    result.skipped.clear()
                    return result

        try:
            os.rename(temp_path, new_path)
            result.successes.append((entry.file_path, final_name))
            phase2_succeeded.append((entry, new_path))
        except Exception as e:
            result.errors.append((entry.file_path, final_name, f"重新命名失敗: {e}"))
            _rollback_all(phase1_moved, phase2_succeeded, phase2_skipped)
            result.successes.clear()
            result.skipped.clear()
            return result

    if progress_callback:
        progress_callback(total_steps, total_steps, "完成")

    return result


def _rollback_all(
    phase1_moved: list[RenameEntry],
    phase2_succeeded: list[tuple[RenameEntry, str]],
    phase2_skipped: set[str],
) -> None:
    # 先將已更名為 new_path 的檔案移回 temp_path
    for entry, new_path in reversed(phase2_succeeded):
        if entry.temp_path and os.path.exists(new_path):
            try:
                os.rename(new_path, entry.temp_path)
            except Exception:
                pass

    # 再將所有暫存檔案移回原始檔名（略過已在跳過階段還原的檔案）
    for entry in reversed(phase1_moved):
        if entry.file_path in phase2_skipped:
            continue
        if entry.temp_path and os.path.exists(entry.temp_path):
            if not os.path.exists(entry.file_path):
                try:
                    os.rename(entry.temp_path, entry.file_path)
                except Exception:
                    pass


def _rollback_temp(temp_entries: list[tuple[str, RenameEntry]]) -> None:
    for temp_path, entry in reversed(temp_entries):
        if os.path.exists(temp_path):
            original = entry.file_path
            if not os.path.exists(original):
                try:
                    os.rename(temp_path, original)
                except Exception:
                    pass
