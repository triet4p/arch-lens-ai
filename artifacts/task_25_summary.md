# Task Summary: Task 25 - GitHub Actions CI

**Sprint:** Sprint 4
**Task:** Add GitHub Actions CI

## Summary of Work
Added a Windows GitHub Actions CI workflow that installs root/frontend/Python dependencies, checks version synchronization, runs backend tests, runs frontend tests and production build, rebuilds the packaged sidecar, runs the packaged smoke path, performs `cargo check`, and builds the NSIS installer.

## Files Modified
* [.github/workflows/ci.yml](.github/workflows/ci.yml) - added the Windows CI verification pipeline with `CARGO_BUILD_JOBS=1`.

## Testing
* **Test File:** Workflow references the verified local commands.
* **Status:** Verified locally
* **Execution Command:** `pwsh scripts/check-version-sync.ps1`, `uv run pytest -v`, `npm run test`, `npm run build`, `uv run python -m scripts.build_sidecar`, `pwsh scripts/smoke-sidecar.ps1`, `cargo check`, `$env:CARGO_BUILD_JOBS='1'; npx tauri build --bundles nsis`

## Additional Notes
* The installer build runs in CI rather than relying on a separate release-only path, so installer regressions surface before tagging.
