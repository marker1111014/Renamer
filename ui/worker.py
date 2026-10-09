import threading
from PyQt5.QtCore import QThread, pyqtSignal
from core.operations import RenameEntry, RenameResult, execute_rename, ConflictAction


class RenameWorker(QThread):
    progress = pyqtSignal(int, int, str)       # (current_step, total_steps, message)
    conflict_needed = pyqtSignal(str, str)     # (new_path, new_name)
    finished_signal = pyqtSignal(object)       # RenameResult

    def __init__(self, entries: list[RenameEntry], parent=None):
        super().__init__(parent)
        self.entries = entries
        self._conflict_event = threading.Event()
        self._conflict_response = ConflictAction.SKIP

    def run(self):
        def conflict_handler(new_path: str, new_name: str) -> ConflictAction:
            self._conflict_event.clear()
            self.conflict_needed.emit(new_path, new_name)
            self._conflict_event.wait()
            return self._conflict_response

        def progress_callback(current: int, total: int, msg: str):
            self.progress.emit(current, total, msg)

        result = execute_rename(
            self.entries,
            conflict_handler=conflict_handler,
            progress_callback=progress_callback,
        )
        self.finished_signal.emit(result)

    def resolve_conflict(self, action: ConflictAction):
        self._conflict_response = action
        self._conflict_event.set()
