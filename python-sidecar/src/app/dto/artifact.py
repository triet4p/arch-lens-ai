from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from src.app.models.artifact import ArtifactType, ArtifactStatus

class ArtifactBase(BaseModel):
    type: ArtifactType
    source_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArtifactCreate(ArtifactBase):
    workspace_id: int

class ArtifactRead(ArtifactBase):
    id: int
    status: ArtifactStatus
    local_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True