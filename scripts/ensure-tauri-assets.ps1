#!/usr/bin/env pwsh

param(
    [switch]$StopNodeProcesses,
    [switch]$ForceRefresh
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
$ICON_SOURCE = Join-Path $ROOT 'assets\app-logo.png'
$ICONS_DIR = Join-Path $ROOT 'src-tauri\icons'
$REQUIRED_ICONS = @(
    '32x32.png',
    '128x128.png',
    '128x128@2x.png',
    'icon.icns',
    'icon.ico'
)

function Assert-Command([string]$name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' was not found in PATH."
    }
}

function Write-Step([string]$message, [string]$color = 'Cyan') {
    Write-Host $message -ForegroundColor $color
}

function Stop-RepoNodeProcesses {
    $rootPattern = [regex]::Escape($ROOT.Path)
    $nodeProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -ieq 'node.exe' -and
        $_.CommandLine -and
        $_.CommandLine -match $rootPattern
    }

    if (-not $nodeProcesses) {
        Write-Step '[TAURI-ASSETS] No repo-owned Node.js processes found.' 'DarkGray'
        return
    }

    Write-Step "[TAURI-ASSETS] Stopping $($nodeProcesses.Count) repo-owned Node.js process(es) before Tauri run..." 'Yellow'
    foreach ($process in $nodeProcesses) {
        Stop-Process -Id $process.ProcessId -Force
    }
}

function Test-IconsCurrent {
    if ($ForceRefresh) {
        return $false
    }

    if (-not (Test-Path $ICON_SOURCE)) {
        throw "Cannot generate Tauri icons because source image is missing: $ICON_SOURCE"
    }

    $sourceTimestamp = (Get-Item $ICON_SOURCE).LastWriteTimeUtc
    foreach ($iconName in $REQUIRED_ICONS) {
        $iconPath = Join-Path $ICONS_DIR $iconName
        if (-not (Test-Path $iconPath)) {
            return $false
        }

        if ((Get-Item $iconPath).LastWriteTimeUtc -lt $sourceTimestamp) {
            return $false
        }
    }

    return $true
}

Assert-Command 'npx'

if ($StopNodeProcesses) {
    Stop-RepoNodeProcesses
}

if (Test-IconsCurrent) {
    Write-Step '[TAURI-ASSETS] Tauri icons already present and current.' 'Green'
    exit 0
}

Write-Step '[TAURI-ASSETS] Generating Tauri icons from assets/app-logo.png ...' 'Cyan'
Push-Location $ROOT
try {
    npx tauri icon $ICON_SOURCE
} finally {
    Pop-Location
}

foreach ($iconName in $REQUIRED_ICONS) {
    $iconPath = Join-Path $ICONS_DIR $iconName
    if (-not (Test-Path $iconPath)) {
        throw "Expected generated icon is missing: $iconPath"
    }
}

Write-Step '[TAURI-ASSETS] Tauri icons ready.' 'Green'
