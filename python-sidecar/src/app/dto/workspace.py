from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.app.dto.artifact import ArtifactRead

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    # Nhận dict từ FE, Service sẽ tự convert sang JSON string để lưu DB
    constraints: Dict[str, Any] = Field(default_factory=dict)

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None

class WorkspaceRead(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Trả về số lượng artifacts để hiển thị ở Dashboard
    artifacts_count: int = 0

    class Config:
        from_attributes = True
        
class WorkspaceDetail(WorkspaceRead):
    artifacts: List[ArtifactRead] = []

    class Config:
        from_attributes = True