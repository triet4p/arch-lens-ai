from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.api import deps
from src.app.api.v1.endpoints import settings as settings_endpoints
from src.app.dto.settings import AISettingsRead


class StubAISettingsService:
    async def get_settings(self):
        return AISettingsRead.model_validate(
            {
                'active_provider': 'ollama',
                'provider_configs': {'ollama': {'base_url': 'http://127.0.0.1:11434'}},
                'keys_status': {'ollama': False, 'openai': True, 'anthropic': False},
                'task_routing': {'default': 'ollama', 'summary': 'ollama', 'chat': 'ollama', 'trend': 'openai', 'code': 'openai'},
            }
        )

    async def update_settings(self, dto):
        if dto.task_routing_update.get('default') == 'invalid':
            raise ValueError('Unsupported provider: invalid')
        return await self.get_settings()


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(settings_endpoints.router, prefix='/settings')
    app.dependency_overrides[deps.get_ai_settings_service] = lambda: StubAISettingsService()
    return TestClient(app)


def test_get_ai_settings_returns_payload():
    client = create_test_client()

    response = client.get('/settings/ai')

    assert response.status_code == 200
    payload = response.json()
    assert payload['active_provider'] == 'ollama'
    assert payload['keys_status']['openai'] is True


def test_update_ai_settings_maps_validation_error_to_400():
    client = create_test_client()

    response = client.put('/settings/ai', json={'task_routing_update': {'default': 'invalid'}})

    assert response.status_code == 400
