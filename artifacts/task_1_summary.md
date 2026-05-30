# Task Summary: Sprint 2 Task 1

**Sprint:** Sprint 2
**Task:** Define the analysis domain contract for artifact-level outputs in models and DTOs

## Summary of Work
Defined a stable analysis contract around `AnalysisResult`, added explicit analysis DTOs for full and summary payloads, attached optional analysis summaries to artifact responses, and synced the frontend API types to the new backend contract.

## Files Modified
* [python-sidecar/src/app/models/analysis.py](/f:/arch-lens-ai/python-sidecar/src/app/models/analysis.py) - Expanded the persisted analysis shape with `analysis_kind` and structured extracted data.
* [python-sidecar/src/app/dto/analysis.py](/f:/arch-lens-ai/python-sidecar/src/app/dto/analysis.py) - Added `AnalysisSummaryRead` and `AnalysisRead`.
* [python-sidecar/src/app/dto/artifact.py](/f:/arch-lens-ai/python-sidecar/src/app/dto/artifact.py) - Attached optional analysis summaries to artifacts.
* [python-sidecar/src/app/core/database.py](/f:/arch-lens-ai/python-sidecar/src/app/core/database.py) - Added lightweight schema migration support for new analysis columns.
* [frontend/src/types/api.ts](/f:/arch-lens-ai/frontend/src/types/api.ts) - Synced the frontend contract with analysis DTOs.

## Testing
* **Test File:** [python-sidecar/tests/test_analysis_service.py](/f:/arch-lens-ai/python-sidecar/tests/test_analysis_service.py)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_analysis_service.py tests/test_artifact_analysis_api.py -v`

## Additional Notes
The contract is intentionally split into summary and full analysis DTOs so workspace views can stay lightweight while direct analysis retrieval still exposes full content maps and ToC data.
