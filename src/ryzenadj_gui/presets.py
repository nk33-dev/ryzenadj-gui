"""预设：一组参数值，存成 JSON。"""

import json
import os
from datetime import datetime
from pathlib import Path

from .params import SETTINGS_BY_KEY

Preset = dict[str, float]

DEFAULT_PRESETS: dict[str, Preset] = {
    "省电": {},
    "均衡": {},
    "性能": {},
}


def default_path() -> Path:
    base = os.environ.get("APPDATA") or Path.home()
    return Path(base) / "ryzenadj-gui" / "presets.json"


def _known(values: dict) -> Preset:
    # 丢掉不认识的参数，免得旧版本或手改的文件把程序搞崩
    return {k: float(v) for k, v in values.items() if k in SETTINGS_BY_KEY}


class PresetStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_path()
        self.presets: dict[str, Preset] = self._load()
        # 用户记下的"系统默认"限制，单独存一个文件，不和预设混在一起
        self.defaults_path = self.path.with_name("defaults.json")
        self.defaults: Preset = {}
        self.defaults_saved_at = ""
        if self.defaults_path.exists():
            data = json.loads(self.defaults_path.read_text(encoding="utf-8"))
            self.defaults = _known(data.get("values", {}))
            self.defaults_saved_at = data.get("saved_at", "")

    def _load(self) -> dict[str, Preset]:
        if not self.path.exists():
            return {name: dict(values) for name, values in DEFAULT_PRESETS.items()}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {name: _known(values) for name, values in data.items()}

    def save_defaults(self, values: Preset) -> None:
        self.defaults = dict(values)
        self.defaults_saved_at = datetime.now().isoformat(sep=" ", timespec="seconds")
        self.defaults_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"saved_at": self.defaults_saved_at, "values": self.defaults}
        text = json.dumps(data, ensure_ascii=False, indent=2)
        self.defaults_path.write_text(text, encoding="utf-8")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(self.presets, ensure_ascii=False, indent=2)
        self.path.write_text(text, encoding="utf-8")

    def names(self) -> list[str]:
        return list(self.presets)

    def get(self, name: str) -> Preset:
        return dict(self.presets[name])

    def put(self, name: str, values: Preset) -> None:
        self.presets[name] = dict(values)
        self.save()

    def delete(self, name: str) -> None:
        self.presets.pop(name, None)
        self.save()
