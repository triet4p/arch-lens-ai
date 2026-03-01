#!/usr/bin/env pwsh
# run-dev.ps1 - Khởi động môi trường dev Tauri
# Usage: ./scripts/run-dev.ps1 [-RebuildSidecar]

param(
    [switch]$RebuildSidecar
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $ROOT

Write-Host ''

# ── Rebuild sidecar (optional) ────────────────────────────────────────────────
if ($RebuildSidecar) {
    Write-Host '[DEV-SCRIPT] 🛠️  Found flag -RebuildSidecar. Rebuilding Python backend...' -ForegroundColor Yellow
    Write-Host '-----------------------------------------------------------------------'

    Set-Location (Join-Path $ROOT 'python-sidecar')
    uv run python -m scripts.build_sidecar
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[DEV-SCRIPT] ❌ Build Failed! Exiting...' -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Set-Location $ROOT

    Write-Host '[DEV-SCRIPT] ✅ Build Sidecar Completed.' -ForegroundColor Green
    Write-Host ''
} else {
    Write-Host '[DEV-SCRIPT] ℹ️  Skipping Sidecar build (Use -RebuildSidecar to force build)' -ForegroundColor Cyan
}

# ── Start Tauri dev ───────────────────────────────────────────────────────────
Write-Host '[DEV-SCRIPT] 🚀 Starting Tauri Dev Environment...' -ForegroundColor Cyan
Write-Host '-----------------------------------------------------------------------'

# Tự động sinh icon cho các nền tảng từ file ảnh gốc
npx tauri icon assets/app-logo.png

# Khởi động Tauri (Tauri sẽ tự gọi frontend dev server)
npx tauri dev
