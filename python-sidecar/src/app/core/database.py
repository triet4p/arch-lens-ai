from typing import Any, Generator
from sqlmodel import SQLModel, create_engine, Session
from src.app.core.config import settings

# check_same_thread=False bắt buộc cho SQLite trong FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

def init_db():
    """Tạo tất cả các bảng trong database khi khởi động"""
    SQLModel.metadata.create_all(engine)
    
def get_session() -> Generator[Session, Any, None]:
    """Dependency Injection cho FastAPI routes"""
    with Session(engine) as session:
        yield session