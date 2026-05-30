# Sprint 2 Plan

## Sprint Goal

Turn artifact ingestion into a usable analysis workflow by adding persisted analysis execution, result retrieval, and frontend rendering.

## Atomic Tasks

Status legend: [ ] pending / [~] in progress / [x] done

- [x] Define the analysis domain contract for artifact-level outputs in models and DTOs.
- [x] Add repository operations for creating, updating, and reading analysis records.
- [x] Implement a backend analysis service for local documents that converts source files into normalized markdown.
- [x] Implement a backend analysis service for GitHub artifacts that derives stack, health, and risk metadata from stored ingestion results.
- [x] Implement a backend analysis service for ArXiv artifacts that extracts structured paper metadata from downloaded content.
- [x] Add artifact analysis API endpoints and status transitions from `PENDING` to terminal states.
- [x] Replace the frontend `Analyze` placeholder with real API mutations and loading states.
- [x] Render analysis summaries on artifact cards and workspace detail views.
- [x] Add focused backend tests for analysis service and endpoint behavior.

## Notes / Blockers

Completed with a deterministic analysis pipeline rather than agent-driven reasoning. The next sprint can build on these persisted results for workspace-level cross-verification.
