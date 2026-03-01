import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_env_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        # Dev mode: src/app/core/config.py -> up 3 levels
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_path, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Arch Lens AI"
    API_V1_STR: str = '/api/v1'
    HOST: str = "127.0.0.1"
    PORT: int = 14201
    
    DATABASE_URL: str = "sqlite:///arch_lens.db"
    
    LOGGING_LEVEL: str = 'INFO'
    LOGGING_HANDLER: str = 'console'
    LOGGING_FILE_DIR: str = '~/.arch_lens/logs'
    
    # Đổi tên thư mục lưu trữ sang arch_lens
    WORKSPACE_STORAGE_DIR: str = '~/.arch_lens/workspace'

    ARXIV_MAX_WAIT_TIME_SECONDS: float = 3.5
    ARXIV_HTTP_TIMEOUT_SECONDS: float = 30.0
    ARXIV_HTTP_MAX_CONNECTIONS: int = 10
    ARXIV_HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 5

    WATCHDOG_TIMEOUT_SECONDS: int = 120
    WATCHDOG_CHECK_INTERVAL_SECONDS: float = 5.0

    model_config = SettingsConfigDict(
        env_file=get_env_path(),
        env_ignore_empty=True,
        extra='ignore'
    )
    
settings = Settings()

# Đảm bảo thư mục lưu trữ tồn tại ngay khi khởi động
os.makedirs(os.path.expanduser(settings.WORKSPACE_STORAGE_DIR), exist_ok=True)