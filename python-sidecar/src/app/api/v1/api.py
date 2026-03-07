from fastapi import APIRouter
from src.app.api.v1.endpoints import health, workspace, artifact

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(workspace.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(artifact.router, prefix="/artifacts", tags=["artifacts"])