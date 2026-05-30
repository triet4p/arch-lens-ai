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
$ICON_SOURCE = Join-Path $ROOT 'assets\app-logo.png'
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

if ($RefreshIcons) {
    if (-not (Test-Path $ICON_SOURCE)) {
        throw "Cannot refresh icons because source image is missing: $ICON_SOURCE"
    }

    Write-Step '[DEV-SCRIPT] 🎨 Refreshing Tauri icons from assets/app-logo.png ...'
    npx tauri icon $ICON_SOURCE
} else {
    Write-Step '[DEV-SCRIPT] ℹ️  Skipping icon refresh (use -RefreshIcons to regenerate icons).' 'Cyan'
}

Write-Step '[DEV-SCRIPT] 🚀 Starting Tauri Dev Environment...' 'Cyan'
Write-Host '-----------------------------------------------------------------------'
npx tauri dev
