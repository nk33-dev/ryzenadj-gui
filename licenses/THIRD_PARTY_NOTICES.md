# 第三方组件许可证

RyzenAdj GUI 本身以 Apache License 2.0 发布（见 `LICENSE`）。打包好的程序里还带有以下第三方组件，它们各自遵循自己的许可证。

## RyzenAdj（libryzenadj.dll）

- 许可证：GNU LGPL 3.0，全文见 `LGPL-3.0.txt`，它引用的 GPL 3.0 见 `GPL-3.0.txt`
- 源码：https://github.com/FlyGoat/RyzenAdj
- 本程序未修改该库，使用的是官方 release 中的二进制文件。可以用自己编译的同名 DLL 替换程序目录下 `_internal\libryzenadj.dll`。

## Qt for Python（PySide6、Shiboken6）及 Qt

- 许可证：GNU LGPL 3.0
- 源码：https://code.qt.io/cgit/pyside/pyside-setup.git 、https://code.qt.io/cgit/qt/
- 本程序未修改这些库，相关 DLL 位于程序目录的 `_internal` 文件夹，可以自行替换。

## WinRing0、InpOut32/64

- 随 RyzenAdj 官方 release 一起分发（`WinRing0x64.dll`、`WinRing0x64.sys`、`inpoutx64.dll`），许可证见各自的原始发布。

## Python

- 许可证：Python Software Foundation License，全文见 `Python-LICENSE.txt`
- 源码：https://www.python.org/

## PyInstaller 引导程序

- 许可证：GPL 2.0，附带例外条款，允许将其与任意许可证的程序一起分发
- 源码：https://github.com/pyinstaller/pyinstaller
