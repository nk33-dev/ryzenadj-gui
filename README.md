# RyzenAdj GUI

[RyzenAdj](https://github.com/FlyGoat/RyzenAdj) 的 Windows 图形界面。可以调整 AMD Ryzen 移动处理器的功耗和温度限制，实时查看功耗、温度、频率，还能把常用配置存成预设一键切换。

## 运行

先安装 [uv](https://docs.astral.sh/uv/)，然后双击 `run.bat`。

脚本会自动从 RyzenAdj 官方 release 下载所需的 DLL 和驱动到 `vendor/`、安装依赖，再启动程序。程序需要管理员权限，启动时会弹出 UAC 确认。

- **设置**：勾选要改的参数，填目标值，点"应用"。没勾选的参数保持原样。"当前限制"列是 CPU 现在实际生效的值。
- **监控**：每秒刷新一次功耗、温度、频率。
- **预设**：存的是"勾了哪些参数、各填多少"。默认带"省电 / 均衡 / 性能"三个空预设，按自己的机器填好后点"保存到预设"。预设文件在 `%APPDATA%\ryzenadj-gui\presets.json`。

## 打包成 exe

双击 `build.bat`，生成：

- `dist/RyzenAdjGUI/`：程序目录，整个拷走即可使用
- `dist/RyzenAdjGUI-<版本>-win64.zip`：上面目录的压缩包，用于发布

许可证文件会一起打进去。

## 已知问题

- **WinRing0 驱动可能被拦截。** `WinRing0x64.sys` 在微软的易受攻击驱动阻止列表里，开了"内核隔离 → 易受攻击的驱动程序阻止列表"或被 Defender 隔离时，程序会提示初始化失败。这是 RyzenAdj 本身的依赖问题，需要在 Windows 安全中心里关掉该选项，或给驱动文件加排除项，风险自行评估。
- **设置不会一直保持。** 睡眠唤醒、插拔电源、切换 Windows 电源模式后，BIOS 或厂商软件可能把值改回去，需要重新点"应用"。
- 不同 CPU 支持的参数不一样，不支持的参数应用时会在该行显示原因。

## 许可证

本项目代码以 [Apache License 2.0](LICENSE) 发布。

本项目是非官方工具，与 AMD 及 RyzenAdj 项目无关。运行时用到的第三方组件各有自己的许可证：

| 组件 | 许可证 | 源码 |
|---|---|---|
| RyzenAdj（`libryzenadj.dll`） | LGPL-3.0 | https://github.com/FlyGoat/RyzenAdj |
| PySide6 / Qt | LGPL-3.0 | https://code.qt.io/cgit/pyside/pyside-setup.git |
| WinRing0 | 见其原始发布 | 随 RyzenAdj 分发 |
| InpOut32/64 | 见其原始发布 | 随 RyzenAdj 分发 |
