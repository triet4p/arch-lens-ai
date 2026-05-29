# Sprint 2 Plan

## Sprint Goal

Turn artifact ingestion into a usable analysis workflow by adding persisted analysis execution, result retrieval, and frontend rendering.

## Atomic Tasks

Status legend: [ ] pending / [~] in progress / [x] done

- [ ] Define the analysis domain contract for artifact-level outputs in models and DTOs.
- [ ] Add repository operations for creating, updating, and reading analysis records.
- [ ] Implement a backend analysis service for local documents that converts source files into normalized markdown.
- [ ] Implement a backend analysis service for GitHub artifacts that derives stack, health, and risk metadata from stored ingestion results.
- [ ] Implement a backend analysis service for ArXiv artifacts that extracts structured paper metadata from downloaded content.
- [ ] Add artifact analysis API endpoints and status transitions from `PENDING` to terminal states.
- [ ] Replace the frontend `Analyze` placeholder with real API mutations and loading states.
- [ ] Render analysis summaries on artifact cards and workspace detail views.
- [ ] Add focused backend tests for analysis service and endpoint behavior.

## Notes / Blockers

The current code shows the UI entry point for analysis, but the action is still a placeholder. There is also no committed test suite yet, so backend tests should be introduced as part of this sprint rather than deferred again.
