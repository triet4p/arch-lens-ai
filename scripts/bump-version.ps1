#!/usr/bin/env pwsh
# bump-version.ps1 - Cập nhật version đồng bộ toàn bộ project
# Usage: ./scripts/bump-version.ps1 -Version 0.2.0

param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
$v = $Version

function Update-File([string]$label, [scriptblock]$action) {
    try {
        & $action
        Write-Host "  [  OK  ] $label" -ForegroundColor Green
    } catch {
        Write-Host "  [ FAIL ] $label  ->  $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ''
Write-Host "  Bumping version to $v ..." -ForegroundColor Cyan
Write-Host ''

# ── JSON files ────────────────────────────────────────────────────────────────
foreach ($f in @('package.json', 'frontend/package.json', 'src-tauri/tauri.conf.json')) {
    Update-File $f {
        $path = Join-Path $ROOT $f
        $j = Get-Content $path -Raw | ConvertFrom-Json
        $j.version = $v
        $j | ConvertTo-Json -Depth 100 | Set-Content $path -Encoding utf8NoBOM
    }
}

# ── Lock files ────────────────────────────────────────────────────────────────
# Dùng regex thay thế trực tiếp để tránh lỗi parse với key rỗng "" trong lockfileV3
foreach ($f in @('package-lock.json', 'frontend/package-lock.json')) {
    Update-File $f {
        $path = Join-Path $ROOT $f
        $raw  = Get-Content $path -Raw
        $raw  = $raw -replace '(?m)^  "version": "[^"]+"', "  `"version`": `"$v`""
        Set-Content $path $raw -Encoding utf8NoBOM -NoNewline
    }
}

# ── TOML files ────────────────────────────────────────────────────────────────
foreach ($info in @(
    @{ f = 'src-tauri/Cargo.toml';          section = '[package]' }
    @{ f = 'python-sidecar/pyproject.toml'; section = '[project]' }
)) {
    Update-File $info.f {
        $path  = Join-Path $ROOT $info.f
        $inSec = $false
        $out   = foreach ($l in (Get-Content $path)) {
            if    ($l -eq $info.section)                    { $inSec = $true;  $l }
            elseif($l -match '^\[')                         { $inSec = $false; $l }
            elseif($inSec -and $l -match '^version\s*=')   { "version = `"$v`"" }
            else  { $l }
        }
        Set-Content $path $out -Encoding utf8NoBOM
    }
}

Write-Host ''
Write-Host "  Done. All files bumped to $v." -ForegroundColor Cyan
Write-Host ''
