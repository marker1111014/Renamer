import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.theme import S_BASE, setup_palette, make_icon
from ui.app import RenamerApp


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(S_BASE)
    setup_palette(app)

    icon = make_icon()
    app.setWindowIcon(icon)

    window = RenamerApp()
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
