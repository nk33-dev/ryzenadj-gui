"""主窗口：设置页 + 监控页，顶部是预设切换。"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..params import SETTINGS, Setting
from ..presets import Preset, PresetStore
from ..ryzenadj import RyzenAdj, RyzenAdjError
from .monitor import MonitorPage


class SettingRow:
    """设置页的一行：勾选框 + 数值框 + 当前值 + 结果。没勾的参数不会下发。"""

    def __init__(self, setting: Setting) -> None:
        self.setting = setting
        self.enabled = QCheckBox(setting.label)
        self.spin = QDoubleSpinBox()
        self.spin.setRange(setting.minimum, setting.maximum)
        self.spin.setDecimals(setting.decimals)
        self.spin.setSuffix(f" {setting.unit}")
        self.spin.setEnabled(False)
        self.current = QLabel("—")
        self.result = QLabel()
        self.enabled.toggled.connect(self.spin.setEnabled)


class SettingsPage(QWidget):
    def __init__(self, ry: RyzenAdj, store: PresetStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ry = ry
        self._store = store
        self._rows = [SettingRow(s) for s in SETTINGS]

        self._preset_box = QComboBox()
        self._preset_box.addItems(store.names())
        self._preset_box.activated.connect(lambda _: self._load_preset())
        save_btn = QPushButton("保存到预设")
        save_btn.clicked.connect(self._save_preset)
        save_as_btn = QPushButton("另存为…")
        save_as_btn.clicked.connect(self._save_preset_as)
        delete_btn = QPushButton("删除预设")
        delete_btn.clicked.connect(self._delete_preset)

        preset_bar = QHBoxLayout()
        preset_bar.addWidget(QLabel("预设"))
        preset_bar.addWidget(self._preset_box, 1)
        preset_bar.addWidget(save_btn)
        preset_bar.addWidget(save_as_btn)
        preset_bar.addWidget(delete_btn)

        grid = QGridLayout()
        grid.addWidget(QLabel("参数（勾选的才会应用）"), 0, 0)
        grid.addWidget(QLabel("目标值"), 0, 1)
        grid.addWidget(QLabel("当前限制"), 0, 2)
        for i, row in enumerate(self._rows, start=1):
            grid.addWidget(row.enabled, i, 0)
            grid.addWidget(row.spin, i, 1)
            grid.addWidget(row.current, i, 2)
            grid.addWidget(row.result, i, 3)
        grid.setColumnStretch(3, 1)

        read_btn = QPushButton("读取当前值")
        read_btn.clicked.connect(self.read_current)
        save_default_btn = QPushButton("记为系统默认")
        save_default_btn.setToolTip("把\"当前限制\"一列的值记下来，之后可以一键恢复")
        save_default_btn.clicked.connect(self._save_defaults)
        self._restore_btn = QPushButton("恢复系统默认")
        self._restore_btn.clicked.connect(self._restore_defaults)
        apply_btn = QPushButton("应用")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self.apply)
        buttons = QHBoxLayout()
        buttons.addWidget(save_default_btn)
        buttons.addWidget(self._restore_btn)
        buttons.addStretch(1)
        buttons.addWidget(read_btn)
        buttons.addWidget(apply_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(preset_bar)
        layout.addLayout(grid)
        layout.addStretch(1)
        layout.addLayout(buttons)

        self._load_preset()
        self.read_current()
        self._update_restore_btn()

    def values(self) -> Preset:
        return {r.setting.key: r.spin.value() for r in self._rows if r.enabled.isChecked()}

    def set_values(self, preset: Preset) -> None:
        for r in self._rows:
            checked = r.setting.key in preset
            r.enabled.setChecked(checked)
            if checked:
                r.spin.setValue(preset[r.setting.key])
            r.result.clear()

    def read_current(self) -> None:
        if self._ry.table_ok:
            self._ry.refresh()
        for r in self._rows:
            value = self._ry.read(r.setting.getter)
            r.current.setText(
                "—" if value is None else f"{value:.{r.setting.decimals}f} {r.setting.unit}"
            )
            # 没勾选的行用当前值填上，勾上就能在此基础上微调
            if value is not None and not r.enabled.isChecked():
                r.spin.setValue(value)

    def apply(self) -> None:
        self._write(self.values())

    def _write(self, values: Preset) -> None:
        for r in self._rows:
            if r.setting.key not in values:
                r.result.clear()
                continue
            try:
                self._ry.apply(r.setting.setter, r.setting.to_raw(values[r.setting.key]))
            except (RyzenAdjError, ValueError) as e:
                r.result.setText(f"✗ {e}")
                r.result.setStyleSheet("color: #c62828")
            else:
                r.result.setText("✓ 已应用")
                r.result.setStyleSheet("color: #2e7d32")
        self.read_current()

    def _current_limits(self) -> Preset:
        if self._ry.table_ok:
            self._ry.refresh()
        values = {}
        for s in SETTINGS:
            value = self._ry.read(s.getter)
            # 读不到的、或者是 0 这种明显没启用的值，恢复时写回去没有意义，跳过
            if value is not None and s.in_range(value):
                values[s.key] = round(value, s.decimals)
        return values

    def _save_defaults(self) -> None:
        values = self._current_limits()
        if not values:
            QMessageBox.warning(self, "记为系统默认", "没有读到任何可记录的限制值。")
            return
        lines = "\n".join(
            f"{s.label}：{values[s.key]:g} {s.unit}" for s in SETTINGS if s.key in values
        )
        answer = QMessageBox.question(
            self,
            "记为系统默认",
            "请确认现在是刚开机、没用本程序改过的状态，否则记下的不是真正的默认值。\n\n"
            f"将记录：\n{lines}",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._store.save_defaults(values)
        self._update_restore_btn()

    def _restore_defaults(self) -> None:
        self._write(self._store.defaults)

    def _update_restore_btn(self) -> None:
        if self._store.defaults:
            self._restore_btn.setEnabled(True)
            self._restore_btn.setToolTip(f"记录于 {self._store.defaults_saved_at}")
        else:
            self._restore_btn.setEnabled(False)
            self._restore_btn.setToolTip("还没记录过系统默认值")

    def _load_preset(self) -> None:
        name = self._preset_box.currentText()
        if name:
            self.set_values(self._store.get(name))

    def _save_preset(self) -> None:
        name = self._preset_box.currentText()
        if not name:
            self._save_preset_as()
            return
        self._store.put(name, self.values())

    def _save_preset_as(self) -> None:
        name, ok = QInputDialog.getText(self, "另存为预设", "预设名称：")
        name = name.strip()
        if not ok or not name:
            return
        if name in self._store.names():
            answer = QMessageBox.question(self, "覆盖预设", f"「{name}」已存在，要覆盖吗？")
            if answer != QMessageBox.StandardButton.Yes:
                return
        else:
            self._preset_box.addItem(name)
        self._store.put(name, self.values())
        self._preset_box.setCurrentText(name)

    def _delete_preset(self) -> None:
        name = self._preset_box.currentText()
        if not name:
            return
        answer = QMessageBox.question(self, "删除预设", f"确定删除「{name}」？")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._store.delete(name)
        self._preset_box.removeItem(self._preset_box.currentIndex())
        self._load_preset()


class MainWindow(QMainWindow):
    def __init__(self, ry: RyzenAdj, store: PresetStore) -> None:
        super().__init__()
        self._ry = ry
        self.setWindowTitle("RyzenAdj GUI")

        info = QLabel(
            f"CPU：{ry.family}　SMU 接口版本：{ry.bios_if_ver}"
            + (f"　PM table：0x{ry.table_ver:x}" if ry.table_ok else "")
        )
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        tabs = QTabWidget()
        tabs.addTab(SettingsPage(ry, store), "设置")
        tabs.addTab(MonitorPage(ry), "监控")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(info)
        layout.addWidget(tabs)
        self.setCentralWidget(central)
        self.resize(640, 420)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt 的方法名
        self._ry.close()
        super().closeEvent(event)
