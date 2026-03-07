from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class ArtifactType(str, Enum):
    PAPER = "paper"
    REPO = "repo"
    INTERNAL_DOC = "internal_doc"

class ArtifactStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Artifact(SQLModel, table=True):
    __tablename__ = "artifacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: ArtifactType
    status: ArtifactStatus = Field(default=ArtifactStatus.PENDING)
    source_url: str
    local_path: Optional[str] = None
    metadata_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.metadata_json)
        except: return {}