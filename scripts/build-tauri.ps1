#!/usr/bin/env pwsh

param(
    [string]$Bundles = 'nsis'
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
$env:CARGO_BUILD_JOBS = if ($env:CARGO_BUILD_JOBS) { $env:CARGO_BUILD_JOBS } else { '1' }

Push-Location $ROOT
try {
    & (Join-Path $ROOT 'scripts\ensure-tauri-assets.ps1') -StopNodeProcesses
    npx tauri build --bundles $Bundles
} finally {
    Pop-Location
}
