# Arch Lens AI Plan

## Overview

Arch Lens AI is a local-first desktop application for technical due diligence. The current codebase already delivers the desktop shell, workspace management, and artifact ingestion foundations. The next planning baseline is to move from "artifact collection" to "artifact analysis", then to cross-verification and reporting.

This file is the source of truth for the project plan. Detailed task breakdowns live under `docs/sprint-plans/`.

## Milestones

* [x] **Milestone 1: Desktop foundation and workspace ingestion**
  Tauri shell, Python sidecar, React workspace UI, SQLite persistence, and artifact ingestion for local files, GitHub, and ArXiv.
* [x] **Milestone 2: Single-artifact analysis pipeline**
  Persisted analysis models, backend analysis endpoints, parsing pipeline, and UI rendering for artifact-level due diligence.
* [x] **Milestone 3: Cross-verification and strategic outputs**
  Workspace-level reasoning across artifacts, Tech Radar, and export/reporting flows.
* [ ] **Milestone 4: Hardening and release readiness**
  Automated tests, error handling, provider/settings UX, and packaging stability.

## Active Sprints

No active sprint is currently defined. The next planning step is Sprint 4.

## Completed Sprints

* [Sprint 1](docs/sprint-plans/sprint-1.md) - *Status: Done*
* [Sprint 2](docs/sprint-plans/sprint-2.md) - *Status: Done*
* [Sprint 3](docs/sprint-plans/sprint-3.md) - *Status: Done*

## Backlog / Future Work

* Cross-artifact chat and contextual RAG over workspace data
* Enterprise Tech Radar aggregation views
* Markdown/PDF report export
* AI provider settings and credential management UX
* Backend and frontend automated test coverage
* Better progress reporting for long-running analysis tasks
