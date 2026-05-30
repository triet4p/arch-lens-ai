import asyncio
import json
from pathlib import Path

from src.app.dto.settings import AISettingsUpdate
from src.app.services.settings import AISettingsService


class FakeKeyring:
    def __init__(self):
        self.values: dict[str, str] = {}

    def set_api_key(self, provider: str, key: str):
        self.values[provider] = key

    def get_api_key(self, provider: str):
        return self.values.get(provider)

    def delete_api_key(self, provider: str):
        self.values.pop(provider, None)


def test_ai_settings_service_reads_updates_and_persists(monkeypatch, tmp_path: Path):
    fake_keyring = FakeKeyring()
    monkeypatch.setattr('src.app.services.settings.KeyringManager', fake_keyring)

    settings_path = tmp_path / 'ai-settings.json'
    service = AISettingsService(settings_file=str(settings_path))

    initial = asyncio.run(service.get_settings())
    assert initial.active_provider == 'ollama'
    assert initial.task_routing['default'] == 'ollama'

    updated = asyncio.run(
        service.update_settings(
            AISettingsUpdate.model_validate(
                {
                    'active_provider': 'openai',
                    'config_update': {'openai': {'default_model': 'gpt-5'}},
                    'api_key_update': {'openai': 'secret-key'},
                    'task_routing_update': {'code': 'openai'},
                }
            )
        )
    )

    assert updated.active_provider == 'openai'
    assert updated.provider_configs['openai']['default_model'] == 'gpt-5'
    assert updated.keys_status['openai'] is True
    assert updated.task_routing['code'] == 'openai'

    persisted = json.loads(settings_path.read_text(encoding='utf-8'))
    assert persisted['active_provider'] == 'openai'
    assert persisted['provider_configs']['openai']['default_model'] == 'gpt-5'
