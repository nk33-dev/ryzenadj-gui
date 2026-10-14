"""管理员权限检查与自动提权。"""

import ctypes
import subprocess
import sys


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def relaunch_as_admin() -> bool:
    """弹 UAC 以管理员身份重新启动自己。用户点了"是"返回 True。"""
    exe = sys.executable
    if getattr(sys, "frozen", False):
        args = sys.argv[1:]
    else:
        args = ["-m", "ryzenadj_gui", *sys.argv[1:]]
        # 换成 pythonw，免得提权后多出一个控制台窗口
        if exe.lower().endswith("python.exe"):
            exe = exe[: -len("python.exe")] + "pythonw.exe"
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe, subprocess.list2cmdline(args), None, 1
    )
    return ret > 32
