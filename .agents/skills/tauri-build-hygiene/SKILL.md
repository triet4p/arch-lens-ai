---
name: tauri-build-hygiene
description: Prepare and run Tauri dev/build workflows safely in this repository. Use when running or changing `npx tauri dev`, `npx tauri build`, `cargo check` under `src-tauri/`, CI/release workflows that build the desktop app, or scripts that touch Tauri icons and sidecar packaging. Clear stale repo-owned Node.js processes first, ensure generated icons exist from `assets/app-logo.png`, and prefer the repository PowerShell wrappers over raw Tauri commands.
---

# Tauri Build Hygiene

## Overview

Use the repository scripts instead of calling raw Tauri commands directly. This avoids two recurring failures in this repo:

- orphaned repo-owned `node.exe` processes from prior Vite/Tauri runs consuming RAM
- `cargo check` / `tauri build` failures because `src-tauri/icons/icon.ico` and related generated icons do not exist in a fresh checkout

## Workflow

### 1. Prepare Tauri assets before dev/build/check steps

Run:

```powershell
pwsh scripts/ensure-tauri-assets.ps1
```

Use `-StopNodeProcesses` when preparing for local dev/build runs:

```powershell
pwsh scripts/ensure-tauri-assets.ps1 -StopNodeProcesses
```

This script:

- stops repo-owned `node.exe` processes whose command line points at this repository
- regenerates icons from `assets/app-logo.png` when required icons are missing or stale
- validates that `icon.ico` and the other bundle icons exist before Tauri commands run

Do not kill every Node process on the machine. Use the repo-scoped cleanup logic in `ensure-tauri-assets.ps1`.

### 2. Use the repository wrapper for Tauri installer builds

Run:

```powershell
pwsh scripts/build-tauri.ps1 -Bundles nsis
```

This wrapper:

- runs the asset-prep script with repo Node cleanup
- preserves `CARGO_BUILD_JOBS=1` unless the caller already set it
- calls `npx tauri build --bundles ...`

Use this wrapper in local operator flows and CI/release workflows instead of raw `npx tauri build`.

### 3. Start Tauri dev through the repo script

Run:

```powershell
pwsh scripts/run-dev.ps1
pwsh scripts/run-dev.ps1 -RebuildSidecar
```

`run-dev.ps1` now prepares Tauri assets and clears stale repo-owned Node.js processes before starting `npx tauri dev`.

Use `-RefreshIcons` only when you intentionally want to force-regenerate icons even if they look current.

### 4. Keep CI in the same shape as local

For GitHub Actions that run `cargo check` or `tauri build`:

- call `pwsh scripts/ensure-tauri-assets.ps1` before `cargo check`
- use `pwsh scripts/build-tauri.ps1 -Bundles nsis` for installer creation
- keep `CARGO_BUILD_JOBS=1` on Windows unless there is strong evidence the memory issue is gone

### 5. Treat `assets/app-logo.png` as source of truth

Keep `src-tauri/icons/` ignored. Those files are generated local artifacts, not source files.

For fresh checkouts, always regenerate icons through:

```powershell
pwsh scripts/ensure-tauri-assets.ps1
```

Do not rely on generated icons already being present in CI or on another machine.
