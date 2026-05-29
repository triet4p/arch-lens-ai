# Sprint 1 Plan

## Sprint Goal

Establish the desktop foundation, workspace-centric data model, and artifact ingestion flows needed to collect due diligence inputs locally.

## Atomic Tasks

Status legend: [ ] pending / [~] in progress / [x] done

- [x] Implement Tauri-side sidecar startup and window bootstrap.
- [x] Implement Python sidecar app bootstrap, lifecycle, and health surface.
- [x] Implement SQLite-backed workspace, artifact, analysis, and link models.
- [x] Implement repository and service layers for workspace CRUD.
- [x] Implement workspace list and workspace detail frontend views.
- [x] Implement artifact ingestion for local file upload.
- [x] Implement artifact ingestion for GitHub repository metadata.
- [x] Implement artifact ingestion for ArXiv metadata and PDF download.
- [x] Render ingested artifacts in the workspace UI with lifecycle status badges.

## Notes / Blockers

This sprint is marked done because the repository already contains these capabilities in the live codebase, including `src-tauri/src/lib.rs`, `python-sidecar/src/main.py`, `python-sidecar/src/app/services/`, and `frontend/src/views/`.
