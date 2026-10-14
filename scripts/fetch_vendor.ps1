# 检查 vendor/ 里的 RyzenAdj 运行文件，缺了就从官方 release 下载。
param([string]$Version = "v0.19.0")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$vendor = Join-Path $root "vendor"
$files = "libryzenadj.dll", "WinRing0x64.dll", "WinRing0x64.sys", "inpoutx64.dll"

$missing = $files | Where-Object { -not (Test-Path (Join-Path $vendor $_)) }
if (-not $missing) { exit 0 }

Write-Host "正在下载 RyzenAdj $Version 运行文件..."
$url = "https://github.com/FlyGoat/RyzenAdj/releases/download/$Version/libryzenadj-win64.zip"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("ryzenadj-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    $zip = Join-Path $tmp "libryzenadj-win64.zip"
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $tmp
    New-Item -ItemType Directory -Force -Path $vendor | Out-Null
    foreach ($f in $files) { Copy-Item (Join-Path $tmp $f) $vendor -Force }
} finally {
    Remove-Item $tmp -Recurse -Force
}
Write-Host "已放到 $vendor"
