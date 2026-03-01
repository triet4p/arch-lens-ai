from fastapi import APIRouter
from src.app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

# Sau này sẽ thêm:
# api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
# api_router.include_router(settings.router, prefix='/settings', tags=['settings'])