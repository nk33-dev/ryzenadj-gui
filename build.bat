@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "ROOT=%CD%"
set "APP=RyzenAdjGUI"

where uv >nul 2>nul || (
    echo 找不到 uv，请先安装：https://docs.astral.sh/uv/
    goto :fail
)

powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_vendor.ps1 || goto :fail
uv sync || goto :fail
for /f %%v in ('uv version --short') do set "VERSION=%%v"

echo 正在打包 %APP% %VERSION% ...
uv run pyinstaller --noconfirm --clean --windowed --uac-admin ^
    --name %APP% ^
    --paths "%ROOT%\src" ^
    --add-binary "%ROOT%\vendor\*;." ^
    --distpath "%ROOT%\dist" --workpath "%ROOT%\build" --specpath "%ROOT%\build" ^
    scripts\pyinstaller_entry.py || goto :fail

set "OUT=%ROOT%\dist\%APP%"

rem WinRing0 只在 exe 所在目录找驱动
copy /y vendor\WinRing0x64.sys "%OUT%\" >nul || goto :fail

rem 随程序附上本项目和第三方组件的许可证
mkdir "%OUT%\licenses" 2>nul
copy /y LICENSE "%OUT%\LICENSE.txt" >nul || goto :fail
copy /y licenses\* "%OUT%\licenses\" >nul || goto :fail
for /f "delims=" %%p in ('uv run python -c "import sys; print(sys.base_prefix)"') do (
    copy /y "%%p\LICENSE.txt" "%OUT%\licenses\Python-LICENSE.txt" >nul || goto :fail
)

rem 用系统自带的 tar 打 zip，Git 带的 tar 不支持 zip
set "ZIP=%ROOT%\dist\%APP%-%VERSION%-win64.zip"
del /q "%ZIP%" 2>nul
"%SystemRoot%\System32\tar.exe" -a -c -f "%ZIP%" -C "%ROOT%\dist" %APP% || goto :fail

echo.
echo 打包完成：
echo   程序目录  %OUT%
echo   发布压缩包 %ZIP%
goto :end

:fail
echo.
echo 打包失败。
call :pause_if_double_clicked
exit /b 1

:end
call :pause_if_double_clicked
exit /b 0

:pause_if_double_clicked
echo %cmdcmdline% | find /i "%~nx0" >nul && pause
exit /b 0
