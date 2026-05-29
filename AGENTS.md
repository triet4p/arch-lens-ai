# AGENTS.md (a.k.a. CLAUDE.md)

This file gives repository-specific guidance to coding agents working in `arch-lens-ai`.

---

## Project Goal

**Arch Lens AI** is a local-first desktop app for technical due diligence.

The product combines:
- **Tauri v2 / Rust** for the desktop shell and sidecar orchestration
- **React 19 + TypeScript** for the UI
- **FastAPI + SQLModel + PydanticAI** in a Python sidecar for business logic, persistence, and future analysis agents

The current product direction is workspace-centric:
- users create **Workspaces**
- attach **Artifacts** from local files, GitHub repos, and ArXiv papers
- later run deeper analysis against that collected context

---

## Current Status

What is implemented in the current codebase:
- Tauri desktop shell starts a Python sidecar and polls backend health on port `14201`
- Workspace dashboard and workspace detail views exist in the frontend
- Workspace CRUD API exists in the Python sidecar
- Artifact ingestion exists for:
  - local file upload
  - GitHub repository metadata fetch
  - ArXiv metadata fetch and PDF download
- SQLite persistence is wired through SQLModel repositories/services
- artifact records are created with `PENDING` status and rendered in the UI

What is not finished yet:
- the "Analyze" action is still a placeholder in the frontend
- deep PydanticAI analysis flows are not wired end to end
- Tech Radar, report export, and cross-verification features are not implemented yet
- there is currently no committed automated test suite in the repository

---

## Repository Layout

```text
arch-lens-ai/
├── frontend/         # React 19 + Vite + TypeScript UI
├── python-sidecar/   # FastAPI sidecar, services, repositories, models
├── src-tauri/        # Tauri v2 Rust shell and sidecar launcher
├── scripts/          # PowerShell automation scripts
├── docs/             # Product, architecture, and implementation notes
└── assets/           # Branding and static assets
```

Key entry points:
- `frontend/src/App.tsx`
- `python-sidecar/src/main.py`
- `python-sidecar/src/app/api/v1/api.py`
- `src-tauri/src/lib.rs`
- `scripts/run-dev.ps1`

---

## Commands

### Install dependencies

```bash
# Root dependencies (Tauri CLI and root plugins)
npm install

# Frontend dependencies
cd frontend
npm install

# Python sidecar dependencies
cd ../python-sidecar
uv sync
```

### Run the desktop app

```bash
# From repo root: rebuild the Python sidecar, then start Tauri dev
pwsh scripts/run-dev.ps1 -RebuildSidecar

# From repo root: start dev without rebuilding the sidecar binary
pwsh scripts/run-dev.ps1
```

### Work on the Python sidecar directly

```bash
cd python-sidecar

# Run the FastAPI sidecar directly
uv run python src/main.py

# Build the packaged sidecar binary used by Tauri
uv run python -m scripts.build_sidecar
```

### Work on the frontend directly

```bash
cd frontend

npm run dev
npm run lint
npm run build
```

### Tauri / Rust checks

```bash
cd src-tauri

cargo check
```

### Tests

```bash
# There is no committed test suite yet.
# When adding backend tests, place them under python-sidecar/tests/
cd python-sidecar
uv run pytest -v
```

### Versioning

```bash
# From repo root
pwsh scripts/bump-version.ps1 -Version 0.2.0
```

---

## Operational Rules

- **Primary runtime model:** This is a **desktop app**, not a standalone web app and not a backend-only service.
- **Python version:** Use **Python 3.13** for sidecar work, matching `python-sidecar/pyproject.toml`.
- **Package managers:** Use `uv` for Python, `npm` for frontend/root JS dependencies, and Cargo through the existing Tauri/Rust setup.
- **PowerShell scripts:** Use `pwsh` for repository automation scripts under `scripts/`.
- **Backend structure:** Keep FastAPI routers thin. Put business logic in `python-sidecar/src/app/services/` and persistence logic in `python-sidecar/src/app/repositories/`.
- **Frontend state:** Server state belongs in TanStack Query hooks. UI-only state belongs in Zustand.
- **API contracts:** When changing backend DTOs, update `frontend/src/types/api.ts` in the same task.
- **Sidecar port:** Preserve port `14201` unless the whole integration is being intentionally changed.
- **Imports:** The live Python code currently uses absolute imports rooted at `src.app...`. Preserve the existing import style in touched modules and do not introduce parent relative imports.
- **Status-driven UX:** Artifact lifecycle is already modeled with statuses such as `PENDING`; preserve that model when adding analysis flows.
- **Scope discipline:** Follow the current workspace/artifact architecture. Do not reintroduce the older paper-centric structure.

---

## Editing Guidance

- Prefer extending the existing layers instead of inventing parallel ones.
- Reuse the current route grouping:
  - `health`
  - `workspaces`
  - `artifacts`
- Reuse the current UI split:
  - `views/` for page-level screens
  - `components/layout/` for shell/layout
  - `components/workspace/` for workspace/artifact UI
- When touching ingestion behavior, check:
  - `python-sidecar/src/app/services/ingestion/`
  - `python-sidecar/src/app/services/artifact.py`
  - `docs/Ingestion-Update-2026-03-07.md`

---

## Skills

- Use the `manage-plans` skill for sprint plans, feature plans, and larger scoped work.
- Use the `implement-atomic-task` skill for single-task implementation work and artifact creation.

---

## Commit Message Standard

**Subject line**:

```text
feat|fix|chore|docs|refactor: short message
```

**Description bullets**:
- what changed
- why it changed
- verification or test results, with specific file references when relevant
