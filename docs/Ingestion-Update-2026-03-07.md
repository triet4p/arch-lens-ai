# Ingestion System Update (2026-03-07)

## Changes Overview

### 1. File Upload Fixes (Backend)
- **FastAPI Parameter Ordering**: Fixed `upload_local_file` endpoint in [artifact.py](../python-sidecar/src/app/api/v1/endpoints/artifact.py) to follow Python's requirements for non-default arguments following default ones.
- **Multipart Handling**: Removed manual `Content-Type: application/json` from Axios client in [axios.ts](../frontend/src/lib/axios.ts) to allow the browser to automatically set the proper `multipart/form-data` boundary for file uploads.
- **Path Resolution**: Centralized `~` path expansion using Pydantic's `model_post_init` in [config.py](../python-sidecar/src/app/core/config.py) to ensure consistent storage paths across different OS environments.

### 2. Database & DTO Conflict Resolution
- **SQLAlchemy Conflict**: Resolved a naming conflict between the SQLAlchemy internal `metadata` attribute and the DTO `metadata` field.
- **DTO Mapping**: Updated `ArtifactService` and `WorkspaceService` to use `model_dump()` before validation. This ensures clean mapping from DB models to API responses while correctly parsing the `metadata_json` string into a structured dictionary.

### 3. Artifact Lifecycle Management
- **Initial Status**: Set default status for newly ingested artifacts (Local, ArXiv, GitHub) to `PENDING`.
- **UI Interaction**: Ensured the "Analyze" button appears on the [ArtifactCard.tsx](../frontend/src/components/workspace/ArtifactCard.tsx) for documents with `PENDING` status, allowing the user to trigger secondary processing (PyMuPDF, MarkItDown, etc.).

## Components Modified
- **Frontend**: 
    - [axios.ts](../frontend/src/lib/axios.ts)
    - [useArtifacts.ts](../frontend/src/hooks/useArtifacts.ts)
    - [ArtifactCard.tsx](../frontend/src/components/workspace/ArtifactCard.tsx)
- **Backend (Python Sidecar)**: 
    - [config.py](../python-sidecar/src/app/core/config.py)
    - [artifact.py (API)](../python-sidecar/src/app/api/v1/endpoints/artifact.py)
    - [artifact.py (Service)](../python-sidecar/src/app/services/artifact.py)
    - [workspace.py (Service)](../python-sidecar/src/app/services/workspace.py)

## Current Status
- ✅ Local File Upload (PDF, DOCX, MD)
- ✅ DB Linking & Persistence
- ✅ Correct UI Status Rendering
- ⏳ Secondary Analysis (Triggered by Analyze Button)
