from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


ProviderName = Literal["ollama", "openai", "anthropic"]
TaskName = Literal["default", "summary", "chat", "trend", "code"]


class AISettingsRead(BaseModel):
    active_provider: ProviderName
    provider_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    keys_status: Dict[str, bool] = Field(default_factory=dict)
    task_routing: Dict[str, str] = Field(default_factory=dict)


class AISettingsUpdate(BaseModel):
    active_provider: ProviderName | None = None
    config_update: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    api_key_update: Dict[str, str] = Field(default_factory=dict)
    keys_to_delete: list[str] = Field(default_factory=list)
    task_routing_update: Dict[str, str] = Field(default_factory=dict)
