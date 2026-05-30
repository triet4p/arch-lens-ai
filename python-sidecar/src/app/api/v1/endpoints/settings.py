from fastapi import APIRouter, HTTPException

from src.app.api.deps import AISettingsServiceDep
from src.app.dto.settings import AISettingsRead, AISettingsUpdate

router = APIRouter()


@router.get("/ai", response_model=AISettingsRead)
async def get_ai_settings(service: AISettingsServiceDep):
    return await service.get_settings()


@router.put("/ai", response_model=AISettingsRead)
async def update_ai_settings(dto: AISettingsUpdate, service: AISettingsServiceDep):
    try:
        return await service.update_settings(dto)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
