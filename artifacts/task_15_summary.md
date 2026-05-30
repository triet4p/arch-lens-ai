# Task Summary: Task 15

**Sprint:** Sprint 3
**Task:** Add report export for markdown output

## Summary of Work
Added markdown report generation in the backend and wired a frontend export action that downloads the current workspace review as a `.md` file.

## Files Modified
* [python-sidecar/src/app/services/review.py](python-sidecar/src/app/services/review.py) - Added markdown report rendering.
* [python-sidecar/src/app/api/v1/endpoints/workspace.py](python-sidecar/src/app/api/v1/endpoints/workspace.py) - Added the markdown export endpoint.
* [frontend/src/hooks/useWorkspaceReview.ts](frontend/src/hooks/useWorkspaceReview.ts) - Added the export mutation and download helper.
* [frontend/src/components/workspace/WorkspaceReviewPanel.tsx](frontend/src/components/workspace/WorkspaceReviewPanel.tsx) - Added the export button.

## Testing
* **Test File:** [python-sidecar/tests/test_workspace_review_api.py](python-sidecar/tests/test_workspace_review_api.py)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_workspace_review_service.py tests/test_workspace_review_api.py tests/test_analysis_service.py tests/test_artifact_analysis_api.py tests/test_workspace_service.py -v`

## Additional Notes
The export is derived from live review data, so it always reflects the latest workspace evidence without an additional persistence step.
