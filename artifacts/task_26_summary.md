# Task Summary: Task 26 - GitHub Actions CD

**Sprint:** Sprint 4
**Task:** Add GitHub Actions CD for GitHub Release publishing

## Summary of Work
Added a tag-driven Windows release workflow that validates version sync, ensures the Git tag matches the Tauri manifest version, rebuilds the sidecar, runs the packaged smoke path, builds the NSIS installer, resolves the generated setup executable, and publishes it to the matching GitHub Release.

## Files Modified
* [.github/workflows/release.yml](.github/workflows/release.yml) - added the tag-triggered release pipeline and GitHub Release asset publication.

## Testing
* **Test File:** Workflow references the verified local commands.
* **Status:** Verified locally
* **Execution Command:** `pwsh scripts/check-version-sync.ps1`, `uv run pytest -v`, `uv run python -m scripts.build_sidecar`, `pwsh scripts/smoke-sidecar.ps1`, `$env:CARGO_BUILD_JOBS='1'; npx tauri build --bundles nsis`

## Additional Notes
* The workflow publishes the generated `*-setup.exe` from the NSIS bundle directory instead of hard-coding a single filename.
