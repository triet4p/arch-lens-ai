# Sprint 4 Plan

## Sprint Goal

Harden the desktop product for real usage and repeatable releases: stabilize packaged runtime behavior, make export and file handling desktop-native, improve error and progress UX, expand automated coverage, add provider/settings UX, refresh stale docs, and then layer version governance plus GitHub CI/CD release automation on top.

## Atomic Tasks

Status legend: [ ] pending / [~] in progress / [x] done

- [x] Stabilize runtime and packaging: audit `run-dev.ps1`, sidecar build/startup health behavior, packaged-mode file paths, DB migration/cleanup behavior, and add a packaged-mode smoke path beyond plain dev mode.
- [x] Replace the current browser-style markdown download with a desktop-native save dialog and file write flow, including filename rules, overwrite handling, and save-failure UX.
- [x] Improve error handling and progress UX for analyze, review, export, startup, and packaging-sensitive failures so the app does not rely on happy-path behavior.
- [x] Expand automated coverage across backend and frontend, with emphasis on workspace review edge cases, ingestion edge cases, DB migration/cleanup behavior, and the main hooks/screens that currently only build-pass.
- [x] Add provider/settings UX for local and pluggable AI usage, including provider selection, credential input, and task/model routing surfaces needed before deeper agent workflows.
- [x] Refresh README and operator/release docs so roadmap, Python version notes, setup steps, and current feature status match the real codebase.
- [x] Audit the current version surfaces and harden `scripts/bump-version.ps1` so it updates every required file deterministically.
- [x] Define a single release contract covering version source, tag naming, artifact naming, installer naming, and which setup `.exe` asset is published.
- [x] Add GitHub Actions CI for backend tests, frontend build, and Tauri production build on the release branch/tag path.
- [x] Add GitHub Actions CD to create a GitHub Release and upload the generated Windows setup `.exe` asset for the matching version tag.

## Acceptance Gates

- The packaged desktop app starts reliably and passes a repeatable smoke flow: create workspace, ingest artifact, analyze artifact, review workspace, export report.
- Report export uses a desktop-native save path instead of a browser-style download target.
- User-visible failures for analyze, review, export, and startup/package issues are surfaced clearly in the UI.
- Test coverage is broad enough that the main runtime and packaging-sensitive paths can be changed without flying blind.
- Provider/settings UX exists and is usable enough to support the next AI-heavy milestone.
- `README.md` and release/operator docs no longer contradict the actual repo state.
- A version bump updates every required manifest consistently, and the release contract is documented.
- A tagged release path can build the Windows installer and publish the matching setup `.exe` to GitHub Releases.

## Notes / Blockers

- `scripts/bump-version.ps1` currently updates more than four files. It touches root `package.json`, `frontend/package.json`, `src-tauri/tauri.conf.json`, two lockfiles, `src-tauri/Cargo.toml`, and `python-sidecar/pyproject.toml`. The release workflow should not be designed around an incorrect assumption about only four version surfaces.
- CI/CD should not publish releases until the version contract is explicit. Otherwise the repo will drift between tags, installer filenames, Tauri metadata, and Python/package manifests.
- CI/CD is part of Sprint 4 release readiness, but it comes after runtime stability and version governance, not instead of them.
- Verified in the repository with local backend tests, frontend tests, frontend production build, packaged sidecar smoke path, `cargo check`, and an NSIS installer build using `CARGO_BUILD_JOBS=1` to avoid Windows-side release build memory failures.
