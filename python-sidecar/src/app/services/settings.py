import json
import os
from copy import deepcopy
from typing import Any

from src.app.core.config import settings
from src.app.core.security import KeyringManager
from src.app.dto.settings import AISettingsRead, AISettingsUpdate


DEFAULT_PROVIDER_CONFIGS: dict[str, dict[str, Any]] = {
    "ollama": {
        "base_url": "http://127.0.0.1:11434",
        "default_model": "qwen3:8b",
        "temperature": 0.1,
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-5-mini",
        "temperature": 0.1,
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "default_model": "claude-3-7-sonnet-latest",
        "temperature": 0.1,
    },
}

DEFAULT_TASK_ROUTING = {
    "default": "ollama",
    "summary": "ollama",
    "chat": "ollama",
    "trend": "openai",
    "code": "openai",
}

VALID_PROVIDERS = set(DEFAULT_PROVIDER_CONFIGS.keys())
VALID_TASKS = set(DEFAULT_TASK_ROUTING.keys())


class AISettingsService:
    def __init__(self, settings_file: str | None = None):
        self.settings_file = settings_file or settings.AI_SETTINGS_FILE

    async def get_settings(self) -> AISettingsRead:
        stored = self._load_settings()
        return AISettingsRead.model_validate(
            {
                "active_provider": stored["active_provider"],
                "provider_configs": stored["provider_configs"],
                "keys_status": {provider: bool(KeyringManager.get_api_key(provider)) for provider in VALID_PROVIDERS},
                "task_routing": stored["task_routing"],
            }
        )

    async def update_settings(self, dto: AISettingsUpdate) -> AISettingsRead:
        stored = self._load_settings()

        if dto.active_provider:
            self._require_provider(dto.active_provider)
            stored["active_provider"] = dto.active_provider

        for provider, config_update in dto.config_update.items():
            self._require_provider(provider)
            provider_config = stored["provider_configs"].setdefault(provider, {})
            provider_config.update(config_update)

        for provider, api_key in dto.api_key_update.items():
            self._require_provider(provider)
            KeyringManager.set_api_key(provider, api_key.strip())

        for provider in dto.keys_to_delete:
            self._require_provider(provider)
            KeyringManager.delete_api_key(provider)

        for task, provider in dto.task_routing_update.items():
            self._require_task(task)
            self._require_provider(provider)
            stored["task_routing"][task] = provider

        self._write_settings(stored)
        return await self.get_settings()

    def _load_settings(self) -> dict[str, Any]:
        if not os.path.exists(self.settings_file):
            default_settings = self._default_payload()
            self._write_settings(default_settings)
            return default_settings

        with open(self.settings_file, "r", encoding="utf-8") as handle:
            raw = json.load(handle)

        merged = self._default_payload()
        merged["active_provider"] = raw.get("active_provider", merged["active_provider"])
        merged["provider_configs"].update(raw.get("provider_configs", {}))
        merged["task_routing"].update(raw.get("task_routing", {}))
        return merged

    def _write_settings(self, payload: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)

    def _default_payload(self) -> dict[str, Any]:
        return {
            "active_provider": "ollama",
            "provider_configs": deepcopy(DEFAULT_PROVIDER_CONFIGS),
            "task_routing": deepcopy(DEFAULT_TASK_ROUTING),
        }

    def _require_provider(self, provider: str) -> None:
        if provider not in VALID_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

    def _require_task(self, task: str) -> None:
        if task not in VALID_TASKS:
            raise ValueError(f"Unsupported task: {task}")
