# Task Summary: Task 21 - Provider and Settings UX

**Sprint:** Sprint 4
**Task:** Add provider/settings UX for local and pluggable AI usage

## Summary of Work
Implemented a full AI settings backend and desktop UI for provider selection, provider config editing, API key management status, and task routing. The backend persists non-secret settings to app config storage and uses the existing keyring abstraction for secrets.

## Files Modified
* [python-sidecar/src/app/dto/settings.py](python-sidecar/src/app/dto/settings.py) - defined AI settings DTOs and routing/provider types.
* [python-sidecar/src/app/services/settings.py](python-sidecar/src/app/services/settings.py) - implemented settings persistence and keyring-backed secret handling.
* [python-sidecar/src/app/api/v1/endpoints/settings.py](python-sidecar/src/app/api/v1/endpoints/settings.py) - added settings read/update endpoints.
* [python-sidecar/src/app/api/v1/api.py](python-sidecar/src/app/api/v1/api.py) - registered the settings router.
* [frontend/src/hooks/useAISettings.ts](frontend/src/hooks/useAISettings.ts) - added query/mutation wrapper for the settings API.
* [frontend/src/views/AISettingsView.tsx](frontend/src/views/AISettingsView.tsx) - added the provider/settings control plane screen.
* [frontend/src/components/layout/Layout.tsx](frontend/src/components/layout/Layout.tsx) - added navigation into the settings screen.

## Testing
* **Test File:** [python-sidecar/tests/test_ai_settings_service.py](python-sidecar/tests/test_ai_settings_service.py), [python-sidecar/tests/test_settings_api.py](python-sidecar/tests/test_settings_api.py), [frontend/src/views/AISettingsView.test.tsx](frontend/src/views/AISettingsView.test.tsx)
* **Status:** Passed
* **Execution Command:** `uv run pytest tests/test_ai_settings_service.py tests/test_settings_api.py -v` and `npm run test`

## Additional Notes
* Settings now live under the per-user config directory introduced in Sprint 4 runtime hardening.
