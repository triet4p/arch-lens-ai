#!/usr/bin/env pwsh
# check-version-sync.ps1 - xác thực các manifest version đã đồng bộ

param(
    [string]$ExpectedVersion
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')

function Get-JsonVersion([string]$relativePath) {
    $path = Join-Path $ROOT $relativePath
    return [string]((Get-Content $path -Raw | ConvertFrom-Json -AsHashtable).version)
}

function Get-PackageLockVersions([string]$relativePath) {
    $path = Join-Path $ROOT $relativePath
    $json = Get-Content $path -Raw | ConvertFrom-Json -AsHashtable
    return @(
        [string]($json.version),
        $(if ($json.packages.ContainsKey('')) { [string]($json.packages[''].version) } else { $null })
    ) | Where-Object { $_ -and $_.Trim().Length -gt 0 }
}

function Get-TomlVersion([string]$relativePath, [string]$section) {
    $path = Join-Path $ROOT $relativePath
    $inSec = $false
    foreach ($line in (Get-Content $path)) {
        if ($line -eq $section) { $inSec = $true; continue }
        if ($line -match '^\[') { $inSec = $false; continue }
        if ($inSec -and $line -match '^version\s*=\s*"([^"]+)"') {
            return [string]$Matches[1]
        }
    }
    throw "Version not found in $relativePath section $section"
}

$versions = [ordered]@{
    'package.json' = @(Get-JsonVersion 'package.json')
    'frontend/package.json' = @(Get-JsonVersion 'frontend/package.json')
    'src-tauri/tauri.conf.json' = @(Get-JsonVersion 'src-tauri/tauri.conf.json')
    'package-lock.json' = @(Get-PackageLockVersions 'package-lock.json')
    'frontend/package-lock.json' = @(Get-PackageLockVersions 'frontend/package-lock.json')
    'src-tauri/Cargo.toml' = @(Get-TomlVersion 'src-tauri/Cargo.toml' '[package]')
    'python-sidecar/pyproject.toml' = @(Get-TomlVersion 'python-sidecar/pyproject.toml' '[project]')
}

$allVersions = @()
foreach ($entry in $versions.GetEnumerator()) {
    foreach ($version in $entry.Value) {
        $allVersions += $version
    }
}

if ($ExpectedVersion) {
    $allVersions += $ExpectedVersion
}

$unique = $allVersions | ForEach-Object { [string]$_ } | Select-Object -Unique
if ($unique.Count -ne 1) {
    Write-Host '[ FAIL ] Version mismatch detected:' -ForegroundColor Red
    foreach ($entry in $versions.GetEnumerator()) {
        Write-Host "  $($entry.Key): $($entry.Value -join ', ')" -ForegroundColor Yellow
    }
    throw "Version surfaces are not synchronized."
}

$resolvedVersion = $unique | Select-Object -First 1
Write-Host "[  OK  ] Version surfaces synchronized at $resolvedVersion" -ForegroundColor Green
