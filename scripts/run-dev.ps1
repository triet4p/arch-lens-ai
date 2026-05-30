#!/usr/bin/env pwsh
# run-dev.ps1 - Khởi động môi trường dev Tauri
# Usage: ./scripts/run-dev.ps1 [-RebuildSidecar] [-RefreshIcons]

param(
    [switch]$RebuildSidecar,
    [switch]$RefreshIcons
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
$SIDECAR_BINARY = Join-Path $ROOT 'src-tauri\binaries\arch-lens-ai-backend-x86_64-pc-windows-msvc.exe'
Set-Location $ROOT

function Assert-Command([string]$name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' was not found in PATH."
    }
}

function Write-Step([string]$message, [string]$color = 'Cyan') {
    Write-Host $message -ForegroundColor $color
}

Write-Host ''
Assert-Command 'uv'
Assert-Command 'npx'

if ($RebuildSidecar) {
    Write-Step '[DEV-SCRIPT] 🛠️  Found flag -RebuildSidecar. Rebuilding Python backend...' 'Yellow'
    Write-Host '-----------------------------------------------------------------------'
    Push-Location (Join-Path $ROOT 'python-sidecar')
    try {
        uv run python -m scripts.build_sidecar
    } finally {
        Pop-Location
    }

    if (-not (Test-Path $SIDECAR_BINARY)) {
        throw "Expected sidecar binary not found at $SIDECAR_BINARY after rebuild."
    }

    Write-Step '[DEV-SCRIPT] ✅ Build Sidecar Completed.' 'Green'
    Write-Host ''
} else {
    if (Test-Path $SIDECAR_BINARY) {
        Write-Step '[DEV-SCRIPT] ℹ️  Reusing existing packaged sidecar binary.' 'Cyan'
    } else {
        Write-Step '[DEV-SCRIPT] ⚠️  No packaged sidecar binary found. Dev may fail until you rebuild with -RebuildSidecar.' 'Yellow'
    }
}

Write-Step '[DEV-SCRIPT] Preparing Tauri assets and clearing stale repo-owned Node.js processes...' 'Cyan'
$ensureArgs = @('-StopNodeProcesses')
if ($RefreshIcons) {
    $ensureArgs += '-ForceRefresh'
}
& pwsh (Join-Path $ROOT 'scripts\ensure-tauri-assets.ps1') @ensureArgs

Write-Step '[DEV-SCRIPT] 🚀 Starting Tauri Dev Environment...' 'Cyan'
Write-Host '-----------------------------------------------------------------------'
npx tauri dev
