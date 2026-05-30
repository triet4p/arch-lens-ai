# Task Summary: Task 17 - Runtime and Packaging Hardening

**Sprint:** Sprint 4
**Task:** Stabilize runtime and packaging

## Summary of Work
Hardened the packaged runtime path by moving sidecar app data to stable per-user directories, adding legacy SQLite migration into the new app-data location, exposing a runtime health endpoint for packaged diagnostics, tightening `run-dev.ps1`, and adding a packaged sidecar smoke script. The sidecar build script was also made Windows-safe and deterministic enough to rebuild the packaged binary for verification.

## Files Modified
* [python-sidecar/src/app/core/config.py](python-sidecar/src/app/core/config.py) - normalized app-data/config/log/workspace paths and SQLite path resolution.
* [python-sidecar/src/app/core/database.py](python-sidecar/src/app/core/database.py) - migrated legacy SQLite database location before engine initialization.
* [python-sidecar/src/app/api/v1/endpoints/health.py](python-sidecar/src/app/api/v1/endpoints/health.py) - added `/api/v1/health/runtime` packaged-runtime diagnostics.
* [scripts/run-dev.ps1](scripts/run-dev.ps1) - improved sidecar rebuild checks and dev bootstrap behavior.
* [python-sidecar/scripts/build_sidecar.py](python-sidecar/scripts/build_sidecar.py) - removed Windows-hostile Unicode logging and invoked PyInstaller through the active interpreter.
* [scripts/smoke-sidecar.ps1](scripts/smoke-sidecar.ps1) - added packaged sidecar smoke verification with a realistic default timeout.

## Testing
* **Test File:** [python-sidecar/tests/test_health_runtime_api.py](python-sidecar/tests/test_health_runtime_api.py)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_health_runtime_api.py -v`
* **Additional Verification:** `uv run python -m scripts.build_sidecar`, `pwsh scripts/smoke-sidecar.ps1`

## Additional Notes
* The verified packaged sidecar smoke path required a 90-second default timeout to account for Windows onefile extraction on first start.
