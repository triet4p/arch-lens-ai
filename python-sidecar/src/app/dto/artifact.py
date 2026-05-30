from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime
from src.app.models.artifact import ArtifactType, ArtifactStatus
from src.app.dto.analysis import AnalysisSummaryRead

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
    analysis: Optional[AnalysisSummaryRead] = None

    model_config = ConfigDict(from_attributes=True)
