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


def _resolve_sqlite_url(database_url: str, app_data_dir: str) -> str:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return database_url

    raw_path = database_url[len(prefix):]
    expanded = os.path.expanduser(raw_path)
    if os.path.isabs(expanded):
        return f"{prefix}{expanded}"

    return f"{prefix}{os.path.join(app_data_dir, expanded)}"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Arch Lens AI"
    API_V1_STR: str = '/api/v1'
    HOST: str = "127.0.0.1"
    PORT: int = 14201
    
    DATABASE_URL: str = "sqlite:///arch_lens.db"

    APP_HOME_DIR: str = "~/.arch_lens"
    APP_CONFIG_DIR: str = "~/.arch_lens/config"
    APP_DATA_DIR: str = "~/.arch_lens/data"
    LOGGING_LEVEL: str = 'INFO'
    LOGGING_HANDLER: str = 'console'
    LOGGING_FILE_DIR: str = '~/.arch_lens/logs'
    WORKSPACE_STORAGE_DIR: str = '~/.arch_lens/workspace'
    AI_SETTINGS_FILE: str = "~/.arch_lens/config/ai-settings.json"

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
    
    def model_post_init(self, __context):
        """Expand ~ paths after model initialization"""
        self.APP_HOME_DIR = os.path.expanduser(self.APP_HOME_DIR)
        self.APP_CONFIG_DIR = os.path.expanduser(self.APP_CONFIG_DIR)
        self.APP_DATA_DIR = os.path.expanduser(self.APP_DATA_DIR)
        self.WORKSPACE_STORAGE_DIR = os.path.expanduser(self.WORKSPACE_STORAGE_DIR)
        self.LOGGING_FILE_DIR = os.path.expanduser(self.LOGGING_FILE_DIR)
        self.AI_SETTINGS_FILE = os.path.expanduser(self.AI_SETTINGS_FILE)
        self.DATABASE_URL = _resolve_sqlite_url(self.DATABASE_URL, self.APP_DATA_DIR)

    @property
    def sqlite_database_path(self) -> str | None:
        prefix = "sqlite:///"
        if not self.DATABASE_URL.startswith(prefix):
            return None
        return self.DATABASE_URL[len(prefix):]


settings = Settings()

# Đảm bảo các thư mục ứng dụng tồn tại ngay khi khởi động
os.makedirs(settings.APP_HOME_DIR, exist_ok=True)
os.makedirs(settings.APP_CONFIG_DIR, exist_ok=True)
os.makedirs(settings.APP_DATA_DIR, exist_ok=True)
os.makedirs(settings.WORKSPACE_STORAGE_DIR, exist_ok=True)
os.makedirs(settings.LOGGING_FILE_DIR, exist_ok=True)
