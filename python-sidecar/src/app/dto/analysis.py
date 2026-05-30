from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AnalysisSummaryRead(BaseModel):
    artifact_id: int
    analysis_kind: str
    summary_markdown: Optional[str] = None
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    scores: dict[str, Any] = Field(default_factory=dict)
    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRead(AnalysisSummaryRead):
    toc: list[dict[str, Any]] = Field(default_factory=list)
    content_map: dict[str, str] = Field(default_factory=dict)
