from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    constraints_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def constraints_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.constraints_json)
        except: return {}

# Bảng Link riêng biệt - Đúng chuẩn SQL
class WorkspaceArtifactLink(SQLModel, table=True):
    __tablename__ = "workspace_artifact_links"
    
    workspace_id: int = Field(
        foreign_key="workspaces.id",
        ondelete="CASCADE",
        primary_key=True
    )
    artifact_id: int = Field(
        foreign_key="artifacts.id",
        ondelete="CASCADE",
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.now)