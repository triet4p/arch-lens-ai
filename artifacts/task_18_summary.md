# Task Summary: Task 18 - Desktop-Native Export

**Sprint:** Sprint 4
**Task:** Replace browser-style report download with desktop-native save flow

## Summary of Work
Replaced the WebView blob-download export path with a Tauri command that opens a native save dialog and writes the markdown report directly to the chosen filesystem path. The frontend export hook now calls that command and reports success, cancellation, or failure through app notifications.

## Files Modified
* [src-tauri/src/lib.rs](src-tauri/src/lib.rs) - added `save_markdown_report` Tauri command backed by a native save dialog and file write.
* [src-tauri/Cargo.toml](src-tauri/Cargo.toml) - added `rfd` for native save dialog support.
* [frontend/src/hooks/useWorkspaceReview.ts](frontend/src/hooks/useWorkspaceReview.ts) - switched export flow from browser download to Tauri invoke and user notifications.

## Testing
* **Test File:** [python-sidecar/tests/test_workspace_review_api.py](python-sidecar/tests/test_workspace_review_api.py)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_workspace_review_api.py -v`
* **Additional Verification:** `npm run build`

## Additional Notes
* The frontend now derives a stable markdown filename before calling the native save command.
