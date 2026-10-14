"""libryzenadj.dll 的 ctypes 封装。"""

import math
import os
import shutil
import sys
from ctypes import CDLL, POINTER, c_float, c_int, c_uint32, c_void_p
from pathlib import Path

from .params import MONITORS, SETTINGS

FAMILY_NAMES = {
    0: "Raven", 1: "Picasso", 2: "Renoir", 3: "Cezanne", 4: "Dali", 5: "Lucienne",
    6: "Vangogh", 7: "Rembrandt", 8: "Mendocino", 9: "Phoenix Point", 10: "Hawk Point",
    11: "Dragon Range", 12: "Krackan Point", 13: "Strix Point", 14: "Strix Halo",
    15: "Fire Range",
}

ERROR_MESSAGES = {
    -1: "这款 CPU 不支持该参数",
    -2: "SMU 响应超时",
    -3: "SMU 不支持该命令",
    -4: "SMU 拒绝了该值",
    -5: "内存访问失败",
}


class RyzenAdjError(Exception):
    pass


def vendor_dir() -> Path:
    # 打包后 DLL 在 PyInstaller 的 _internal 目录里；开发时在项目根目录的 vendor/
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2] / "vendor"


def _place_winring0_driver(src_dir: Path) -> None:
    # WinRing0 只在当前进程 exe 所在目录找 .sys。venv 里的 python.exe 只是个转发器，
    # 真正跑的是基础解释器，所以两个目录都放一份。
    driver = src_dir / "WinRing0x64.sys"
    base_exe = getattr(sys, "_base_executable", sys.executable)
    for d in {Path(sys.executable).parent, Path(base_exe).parent}:
        target = d / driver.name
        if not target.exists():
            shutil.copyfile(driver, target)


class RyzenAdj:
    def __init__(self, dll_dir: Path | None = None) -> None:
        dll_dir = dll_dir or vendor_dir()
        if not (dll_dir / "libryzenadj.dll").exists():
            raise RyzenAdjError(f"找不到 libryzenadj.dll（查找位置：{dll_dir}）")
        _place_winring0_driver(dll_dir)
        self._dll_dir_handle = os.add_dll_directory(str(dll_dir))
        # 库里用裸 LoadLibrary("inpoutx64.DLL") 加载，不认 add_dll_directory，
        # 先按完整路径载入，之后按名字就能直接拿到已加载的模块
        self._inpout = CDLL(str(dll_dir / "inpoutx64.dll"))
        self._lib = lib = CDLL(str(dll_dir / "libryzenadj.dll"))

        lib.init_ryzenadj.restype = c_void_p
        lib.cleanup_ryzenadj.argtypes = [c_void_p]
        lib.cleanup_ryzenadj.restype = None
        for name in ("get_cpu_family", "get_bios_if_ver", "init_table", "refresh_table"):
            getattr(lib, name).argtypes = [c_void_p]
            getattr(lib, name).restype = c_int
        lib.get_table_ver.argtypes = [c_void_p]
        lib.get_table_ver.restype = c_uint32
        lib.get_table_values.argtypes = [c_void_p]
        lib.get_table_values.restype = POINTER(c_float)
        for s in SETTINGS:
            getattr(lib, s.setter).argtypes = [c_void_p, c_uint32]
            getattr(lib, s.setter).restype = c_int
        for name in {s.getter for s in SETTINGS} | {m.getter for m in MONITORS}:
            getattr(lib, name).argtypes = [c_void_p]
            getattr(lib, name).restype = c_float

        self._ry = lib.init_ryzenadj()
        if not self._ry:
            raise RyzenAdjError(
                "RyzenAdj 初始化失败。可能原因：不是 AMD Ryzen 移动处理器、"
                "没有以管理员身份运行，或 WinRing0 驱动被 Windows 安全中心拦截。"
            )
        self.table_ok = lib.init_table(self._ry) == 0

    @property
    def family(self) -> str:
        return FAMILY_NAMES.get(self._lib.get_cpu_family(self._ry), "未知")

    @property
    def bios_if_ver(self) -> int:
        return self._lib.get_bios_if_ver(self._ry)

    @property
    def table_ver(self) -> int:
        return self._lib.get_table_ver(self._ry)

    def refresh(self) -> bool:
        return self._lib.refresh_table(self._ry) == 0

    def read(self, getter: str) -> float | None:
        value = getattr(self._lib, getter)(self._ry)
        return None if math.isnan(value) else value

    def apply(self, setter: str, raw: int) -> None:
        err = getattr(self._lib, setter)(self._ry, raw)
        if err:
            raise RyzenAdjError(ERROR_MESSAGES.get(err, f"未知错误 {err}"))

    def close(self) -> None:
        # init_table 失败时 cleanup_ryzenadj 会调用空的 UnmapPhysicalMemory 指针而崩溃，
        # 这种情况只能不清理，进程退出时系统会回收
        if self._ry and self.table_ok:
            self._lib.cleanup_ryzenadj(self._ry)
        self._ry = None
