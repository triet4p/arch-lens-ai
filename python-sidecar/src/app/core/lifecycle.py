from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.core.database import init_db
from src.app.core.logger import get_logger

_logger = get_logger("[PythonSidecar - Lifecycle]")

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    _logger.info("🚀 Arch Lens Backend is starting up...")
    init_db()
    await app.state.arxiv_api_state.init_client()
    _logger.info("✅ Startup sequence complete.")
    
    yield

    _logger.info("🛑 Backend is shutting down...")
    await app.state.arxiv_api_state.close_client()