@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

where uv >nul 2>nul || (
    echo 找不到 uv，请先安装：https://docs.astral.sh/uv/
    goto :fail
)

powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_vendor.ps1 || goto :fail
uv sync || goto :fail

rem 不是管理员时程序会弹 UAC 以管理员身份重开自己，这个窗口随即关闭
uv run python -m ryzenadj_gui || goto :fail
exit /b 0

:fail
echo.
echo 启动失败。
pause
exit /b 1
