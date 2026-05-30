#!/usr/bin/env pwsh
# smoke-sidecar.ps1 - packaged sidecar smoke path beyond Tauri dev mode

param(
    [int]$Port = 14201,
    [int]$TimeoutSeconds = 90
)

$ErrorActionPreference = 'Stop'
$ROOT = Resolve-Path (Join-Path $PSScriptRoot '..')
$BINARY = Join-Path $ROOT 'src-tauri\binaries\arch-lens-ai-backend-x86_64-pc-windows-msvc.exe'
$HealthUrl = "http://127.0.0.1:$Port/api/v1/health/runtime"
$ApiRoot = "http://127.0.0.1:$Port/api/v1"

if (-not (Test-Path $BINARY)) {
    throw "Packaged sidecar binary not found at $BINARY. Rebuild it first."
}

Write-Host "[SMOKE] Starting packaged sidecar: $BINARY" -ForegroundColor Cyan
$process = Start-Process -FilePath $BINARY -PassThru -WindowStyle Hidden
$workspaceId = $null
$tempFile = $null

try {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 3
            Write-Host "[SMOKE] Health runtime endpoint responded." -ForegroundColor Green
            $response | ConvertTo-Json -Depth 10
            break
        } catch {
            if ((Get-Date) -ge $deadline) {
                throw "Timed out waiting for packaged sidecar health at $HealthUrl"
            }
        }
    } while ($true)

    $tempFile = Join-Path ([System.IO.Path]::GetTempPath()) "arch-lens-smoke-$([guid]::NewGuid().ToString('N')).md"
    @"
# Sprint 4 Smoke Artifact

- Runtime path
- Analysis flow
- Workspace review flow
"@ | Set-Content -Path $tempFile -Encoding UTF8

    Write-Host "[SMOKE] Creating workspace..." -ForegroundColor Cyan
    $workspace = Invoke-RestMethod `
        -Method Post `
        -Uri "$ApiRoot/workspaces/" `
        -ContentType 'application/json' `
        -Body (@{
            name = "Sprint 4 Smoke $([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
            description = "Packaged sidecar smoke test"
            constraints = @{
                gpu_limit = "24GB VRAM"
                current_stack = "Python/FastAPI"
            }
        } | ConvertTo-Json -Depth 10)
    $workspaceId = $workspace.id

    Write-Host "[SMOKE] Uploading local artifact..." -ForegroundColor Cyan
    $artifact = Invoke-RestMethod `
        -Method Post `
        -Uri "$ApiRoot/artifacts/upload/$workspaceId" `
        -Form @{ file = Get-Item $tempFile }

    Write-Host "[SMOKE] Analyzing artifact $($artifact.id)..." -ForegroundColor Cyan
    $analysis = Invoke-RestMethod -Method Post -Uri "$ApiRoot/artifacts/$($artifact.id)/analyze"
    if (-not $analysis.summary_markdown) {
        throw "Analysis summary was empty."
    }

    Write-Host "[SMOKE] Running workspace review..." -ForegroundColor Cyan
    $review = Invoke-RestMethod -Method Post -Uri "$ApiRoot/workspaces/$workspaceId/review"
    if (-not $review.recommendation.label) {
        throw "Workspace review recommendation was empty."
    }

    Write-Host "[SMOKE] Exporting markdown report..." -ForegroundColor Cyan
    $report = Invoke-RestMethod -Method Get -Uri "$ApiRoot/workspaces/$workspaceId/report.md"
    if (-not ($report -match '^# Workspace Review:')) {
        throw "Workspace report did not contain the expected heading."
    }

    Write-Host "[SMOKE] Fetching tech radar..." -ForegroundColor Cyan
    $radar = Invoke-RestMethod -Method Get -Uri "$ApiRoot/workspaces/radar"
    if ($radar.workspaces_covered -lt 1) {
        throw "Tech radar did not include the smoke workspace."
    }

    Write-Host "[SMOKE] Packaged sidecar business flow passed." -ForegroundColor Green
} finally {
    if ($workspaceId) {
        try {
            Invoke-RestMethod -Method Delete -Uri "$ApiRoot/workspaces/$workspaceId" | Out-Null
        } catch {
            Write-Warning "[SMOKE] Failed to delete smoke workspace ${workspaceId}: $($_.Exception.Message)"
        }
    }

    if ($tempFile -and (Test-Path $tempFile)) {
        Remove-Item -LiteralPath $tempFile -Force
    }

    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
}
