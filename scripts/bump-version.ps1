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

function Assert-Command([string]$name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' was not found in PATH."
    }
}

function Update-File([string]$label, [scriptblock]$action) {
    try {
        & $action
        Write-Host "  [  OK  ] $label" -ForegroundColor Green
    } catch {
        Write-Host "  [ FAIL ] $label  ->  $_" -ForegroundColor Red
        exit 1
    }
}

function Update-JsonVersion([string]$relativePath) {
    Update-File $relativePath {
        $path = Join-Path $ROOT $relativePath
        $json = Get-Content $path -Raw | ConvertFrom-Json
        $json.version = $v
        $json | ConvertTo-Json -Depth 100 | Set-Content $path -Encoding utf8NoBOM
    }
}

function Update-PackageLockVersion([string]$relativePath) {
    Update-File $relativePath {
        $path = Join-Path $ROOT $relativePath
        $nodeScript = @'
const fs = require("fs");
const path = process.argv[1];
const version = process.argv[2];
const lock = JSON.parse(fs.readFileSync(path, "utf8"));
lock.version = version;
if (lock.packages && lock.packages[""]) {
  lock.packages[""].version = version;
}
fs.writeFileSync(path, JSON.stringify(lock, null, 2) + "\n", "utf8");
'@
        $nodeScript | node - $path $v
    }
}

function Update-TomlVersion([string]$relativePath, [string]$section) {
    Update-File $relativePath {
        $path = Join-Path $ROOT $relativePath
        $inSec = $false
        $out = foreach ($line in (Get-Content $path)) {
            if ($line -eq $section) { $inSec = $true; $line; continue }
            if ($line -match '^\[') { $inSec = $false; $line; continue }
            if ($inSec -and $line -match '^version\s*=') { "version = `"$v`""; continue }
            $line
        }
        Set-Content $path $out -Encoding utf8NoBOM
    }
}

Write-Host ''
Write-Host "  Bumping version to $v ..." -ForegroundColor Cyan
Write-Host ''

Assert-Command 'node'
Assert-Command 'pwsh'

foreach ($file in @('package.json', 'frontend/package.json', 'src-tauri/tauri.conf.json')) {
    Update-JsonVersion $file
}

foreach ($file in @('package-lock.json', 'frontend/package-lock.json')) {
    Update-PackageLockVersion $file
}

Update-TomlVersion 'src-tauri/Cargo.toml' '[package]'
Update-TomlVersion 'python-sidecar/pyproject.toml' '[project]'

$checkScript = Join-Path $ROOT 'scripts/check-version-sync.ps1'
if (-not (Test-Path $checkScript)) {
    throw "Version sync check script not found at $checkScript"
}

& $checkScript -ExpectedVersion $v

Write-Host ''
Write-Host "  Done. All files bumped to $v." -ForegroundColor Cyan
Write-Host ''
