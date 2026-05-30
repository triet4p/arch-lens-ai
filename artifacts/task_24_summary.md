# Task Summary: Task 24 - Release Contract Definition

**Sprint:** Sprint 4
**Task:** Define the release contract

## Summary of Work
Created a concrete release contract covering manifest synchronization, tag naming, GitHub Release naming, installer naming, and the exact Windows setup asset selection rule. The contract also records the verified requirement to limit Cargo build parallelism during Windows installer creation.

## Files Modified
* [docs/Release-Contract.md](docs/Release-Contract.md) - documented release source-of-truth rules and operational release sequence.

## Testing
* **Test File:** N/A
* **Status:** Verified against the generated installer path.
* **Execution Command:** `$env:CARGO_BUILD_JOBS='1'; npx tauri build --bundles nsis`

## Additional Notes
* The current contract intentionally targets the Windows NSIS installer only; code signing is still outside Sprint 4 scope.
