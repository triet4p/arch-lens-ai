import json
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Field, SQLModel

class AnalysisResult(SQLModel, table=True):
    __tablename__ = "analysis_results"

    artifact_id: int = Field(
        foreign_key="artifacts.id",
        ondelete="CASCADE",
        primary_key=True
    )
    analysis_kind: str = Field(default="unknown")
    toc_json: str = Field(default="[]")
    content_map_json: str = Field(default="{}")
    extracted_data_json: str = Field(default="{}")
    summary_markdown: Optional[str] = None
    due_diligence_score_json: str = Field(default="{}")
    analyzed_at: datetime = Field(default_factory=datetime.now)

    @property
    def toc_data(self) -> list:
        try:
            return json.loads(self.toc_json)
        except Exception:
            return []

    @property
    def content_data(self) -> dict[str, str]:
        try:
            return json.loads(self.content_map_json)
        except Exception:
            return {}

    @property
    def extracted_data(self) -> dict[str, Any]:
        try:
            return json.loads(self.extracted_data_json)
        except Exception:
            return {}

    @property
    def scores_dict(self) -> dict[str, Any]:
        try:
            return json.loads(self.due_diligence_score_json)
        except Exception:
            return {}
