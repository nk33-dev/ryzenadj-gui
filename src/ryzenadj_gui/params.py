"""界面上能调的参数和能看的监控项。

加新参数只需要往 SETTINGS / MONITORS 里加一行，setter/getter 名字照 ryzenadj.h 抄。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Setting:
    key: str  # 预设文件里用的名字，和 ryzenadj CLI 的长参数一致
    label: str
    unit: str
    setter: str
    getter: str  # 读当前生效的限制值，单位已经是界面单位
    scale: int  # 界面值乘以它才是 setter 要的原始值，比如 W → mW 是 1000
    minimum: float
    maximum: float
    decimals: int = 0

    def to_raw(self, value: float) -> int:
        raw = round(value * self.scale)
        if not 0 <= raw <= 0xFFFFFFFF:
            raise ValueError(f"{self.label} 超出范围：{value}")
        return raw


@dataclass(frozen=True)
class Monitor:
    label: str
    getter: str
    unit: str
    decimals: int = 1


SETTINGS: tuple[Setting, ...] = (
    Setting("stapm-limit", "持续功耗 (STAPM)", "W", "set_stapm_limit", "get_stapm_limit",
            1000, 1, 200, 1),
    Setting("fast-limit", "短时峰值功耗 (PPT Fast)", "W", "set_fast_limit", "get_fast_limit",
            1000, 1, 200, 1),
    Setting("slow-limit", "平均功耗 (PPT Slow)", "W", "set_slow_limit", "get_slow_limit",
            1000, 1, 200, 1),
    Setting("stapm-time", "STAPM 时间常数", "s", "set_stapm_time", "get_stapm_time",
            1, 1, 10000),
    Setting("slow-time", "PPT Slow 时间常数", "s", "set_slow_time", "get_slow_time",
            1, 1, 10000),
    Setting("tctl-temp", "核心温度上限 (Tctl)", "°C", "set_tctl_temp", "get_tctl_temp",
            1, 40, 105),
    Setting("apu-skin-temp", "机身温度上限 (APU STT)", "°C", "set_apu_skin_temp_limit",
            "get_apu_skin_temp_limit", 1, 25, 105),
)

SETTINGS_BY_KEY = {s.key: s for s in SETTINGS}

MONITORS: tuple[Monitor, ...] = (
    Monitor("STAPM 功耗", "get_stapm_value", "W"),
    Monitor("PPT Fast 功耗", "get_fast_value", "W"),
    Monitor("PPT Slow 功耗", "get_slow_value", "W"),
    Monitor("整颗芯片功耗", "get_socket_power", "W"),
    Monitor("核心温度 (Tctl)", "get_tctl_temp_value", "°C"),
    Monitor("机身温度 (APU STT)", "get_apu_skin_temp_value", "°C"),
    Monitor("核显频率", "get_gfx_clk", "MHz", 0),
    Monitor("核显温度", "get_gfx_temp", "°C"),
    Monitor("内存频率", "get_mem_clk", "MHz", 0),
    Monitor("Infinity Fabric 频率", "get_fclk", "MHz", 0),
)
