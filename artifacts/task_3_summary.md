# Task Summary: Sprint 2 Task 3

**Sprint:** Sprint 2
**Task:** Implement a backend analysis service for local documents that converts source files into normalized markdown

## Summary of Work
Implemented deterministic local document analysis using `MarkItDown` for text-like files and `pymupdf4llm` for PDFs. The service extracts markdown, derives a heading-based ToC, builds a section content map, computes lightweight document scores, and persists the result.

## Files Modified
* [python-sidecar/src/app/services/analysis.py](/f:/arch-lens-ai/python-sidecar/src/app/services/analysis.py) - Added local document parsing and analysis logic.

## Testing
* **Test File:** [python-sidecar/tests/test_analysis_service.py](/f:/arch-lens-ai/python-sidecar/tests/test_analysis_service.py)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_analysis_service.py tests/test_artifact_analysis_api.py -v`

## Additional Notes
The implementation stays deterministic and does not depend on any LLM provider, which makes it a solid Sprint 2 baseline.
