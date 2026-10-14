"""预设：一组参数值，存成 JSON。"""

import json
import os
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


class PresetStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_path()
        self.presets: dict[str, Preset] = self._load()

    def _load(self) -> dict[str, Preset]:
        if not self.path.exists():
            return {name: dict(values) for name, values in DEFAULT_PRESETS.items()}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        # 丢掉不认识的参数，免得旧版本或手改的文件把程序搞崩
        return {
            name: {k: float(v) for k, v in values.items() if k in SETTINGS_BY_KEY}
            for name, values in data.items()
        }

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
