"""监控页：每秒刷新一次 PM table。"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from ..params import MONITORS
from ..ryzenadj import RyzenAdj

INTERVAL_MS = 1000


class MonitorPage(QWidget):
    def __init__(self, ry: RyzenAdj, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ry = ry
        layout = QFormLayout(self)
        self._labels: list[QLabel] = []
        for m in MONITORS:
            label = QLabel("—")
            layout.addRow(m.label, label)
            self._labels.append(label)

        self._status = QLabel()
        layout.addRow(self._status)

        self._timer = QTimer(self)
        self._timer.setInterval(INTERVAL_MS)
        self._timer.timeout.connect(self.refresh)
        if ry.table_ok:
            self._timer.start()
            self.refresh()
            # 不同 CPU 的 PM table 字段不一样，读不到的项一直是空的，直接藏起来
            for m, label in zip(MONITORS, self._labels, strict=True):
                if ry.read(m.getter) is None:
                    layout.setRowVisible(label, False)
        else:
            self._status.setText("这台机器读不到 PM table，监控不可用。")

    def refresh(self) -> None:
        if not self._ry.refresh():
            self._status.setText("刷新 PM table 失败")
            return
        self._status.clear()
        for m, label in zip(MONITORS, self._labels, strict=True):
            value = self._ry.read(m.getter)
            label.setText("—" if value is None else f"{value:.{m.decimals}f} {m.unit}")
