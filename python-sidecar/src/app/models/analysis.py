from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class AnalysisResult(SQLModel, table=True):
    __tablename__ = "analysis_results"

    # artifact_id đóng vai trò vừa là PK vừa là FK (Quan hệ 1-1)
    artifact_id: int = Field(
        foreign_key="artifacts.id",
        ondelete="CASCADE",
        primary_key=True
    )
    toc_json: str = Field(default="[]")
    content_map_json: str = Field(default="{}")
    summary_markdown: Optional[str] = None
    due_diligence_score_json: str = Field(default="{}")
    analyzed_at: datetime = Field(default_factory=datetime.now)

    @property
    def toc_data(self) -> list:
        try: return json.loads(self.toc_json)
        except: return []

    @property
    def content_data(self) -> Dict[str, str]:
        try: return json.loads(self.content_map_json)
        except: return {}

    @property
    def scores_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.due_diligence_score_json)
        except: return {}