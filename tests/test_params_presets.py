import json

import pytest

from ryzenadj_gui.params import SETTINGS, SETTINGS_BY_KEY
from ryzenadj_gui.presets import PresetStore


def test_watts_to_milliwatts():
    assert SETTINGS_BY_KEY["stapm-limit"].to_raw(25.5) == 25500


def test_celsius_is_passed_through():
    assert SETTINGS_BY_KEY["tctl-temp"].to_raw(85) == 85


def test_negative_value_rejected():
    with pytest.raises(ValueError):
        SETTINGS_BY_KEY["stapm-limit"].to_raw(-1)


def test_setting_keys_unique():
    assert len(SETTINGS_BY_KEY) == len(SETTINGS)


def test_new_store_has_default_presets(tmp_path):
    store = PresetStore(tmp_path / "presets.json")
    assert store.names() == ["省电", "均衡", "性能"]


def test_preset_roundtrip(tmp_path):
    path = tmp_path / "presets.json"
    PresetStore(path).put("游戏", {"stapm-limit": 35.0, "tctl-temp": 90.0})
    assert PresetStore(path).get("游戏") == {"stapm-limit": 35.0, "tctl-temp": 90.0}


def test_unknown_keys_dropped_on_load(tmp_path):
    path = tmp_path / "presets.json"
    path.write_text(json.dumps({"旧": {"stapm-limit": 20, "no-such-option": 1}}), encoding="utf-8")
    assert PresetStore(path).get("旧") == {"stapm-limit": 20.0}


def test_delete_preset(tmp_path):
    path = tmp_path / "presets.json"
    store = PresetStore(path)
    store.delete("均衡")
    assert "均衡" not in PresetStore(path).names()
