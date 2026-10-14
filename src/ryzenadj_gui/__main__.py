import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .elevate import is_admin, relaunch_as_admin
from .presets import PresetStore
from .ryzenadj import RyzenAdj, RyzenAdjError
from .ui.main_window import MainWindow


def main() -> int:
    if not is_admin() and relaunch_as_admin():
        return 0

    app = QApplication(sys.argv)
    if not is_admin():
        QMessageBox.critical(None, "RyzenAdj GUI", "需要管理员权限才能访问 CPU 的 SMU。")
        return 1
    try:
        ry = RyzenAdj()
    except RyzenAdjError as e:
        QMessageBox.critical(None, "RyzenAdj GUI", str(e))
        return 1

    window = MainWindow(ry, PresetStore())
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
