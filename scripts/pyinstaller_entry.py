# PyInstaller 的入口。__main__.py 里用了相对导入，不能直接拿来打包。
from ryzenadj_gui.__main__ import main

raise SystemExit(main())
