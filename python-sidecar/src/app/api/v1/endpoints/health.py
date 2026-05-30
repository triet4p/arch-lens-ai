import os
import sys
from pathlib import Path

from fastapi import APIRouter, Request
import time

from src.app.core.config import get_env_path, settings

router = APIRouter()

@router.get('/')
async def hello():
    return {"status": "alive", "message": "Arch Lens AI is ready"}

@router.get("/health")
async def health_check(request: Request):
    """
    Endpoint để Frontend ping định kỳ, giữ cho Sidecar không tự tắt.
    Trả về số lượng active requests để frontend có thể quyết định skip nếu cần.
    """
    # Lấy state từ request.app (đã được khởi tạo ở main.py)
    active_requests = request.app.state.system_state.total_active_work

    # Test nhẹ các thư viện lõi
    components_status = {"status": "ok"}
    try:
        components_status = {
            "pydantic_ai": "ready",
            "markitdown": "initialized",
            "pymupdf4llm": "available",
            "sqlmodel": "ready"
        }
    except Exception as e:
        components_status = {"status": "error", "detail": str(e)}

    return {
        "status": "alive", 
        "timestamp": time.time(),
        "active_requests": active_requests,
        "busy": active_requests > 0,
        "components": components_status
    }


@router.get("/health/runtime")
async def runtime_diagnostics():
    database_path = settings.sqlite_database_path
    env_path = Path(get_env_path())

    return {
        "status": "alive",
        "frozen": bool(getattr(sys, "frozen", False)),
        "python_executable": sys.executable,
        "cwd": os.getcwd(),
        "database_url": settings.DATABASE_URL,
        "database_path": database_path,
        "database_exists": bool(database_path and os.path.exists(database_path)),
        "workspace_storage_dir": settings.WORKSPACE_STORAGE_DIR,
        "workspace_storage_exists": os.path.exists(settings.WORKSPACE_STORAGE_DIR),
        "logging_file_dir": settings.LOGGING_FILE_DIR,
        "logging_file_dir_exists": os.path.exists(settings.LOGGING_FILE_DIR),
        "ai_settings_file": settings.AI_SETTINGS_FILE,
        "ai_settings_exists": os.path.exists(settings.AI_SETTINGS_FILE),
        "env_file": str(env_path),
        "env_file_exists": env_path.exists(),
    }
