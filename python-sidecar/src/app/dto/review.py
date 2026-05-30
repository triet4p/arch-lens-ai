from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from src.app.models.artifact import ArtifactStatus, ArtifactType


class ReviewArtifactContext(BaseModel):
    artifact_id: int
    artifact_type: ArtifactType
    status: ArtifactStatus
    title: str
    analysis_kind: Optional[str] = None
    summary_markdown: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    scores: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceReviewInput(BaseModel):
    workspace_id: int
    workspace_name: str
    workspace_description: Optional[str] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[ReviewArtifactContext] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    category: Literal["fit", "evidence", "execution", "risk"]
    title: str
    detail: str
    related_artifact_ids: List[int] = Field(default_factory=list)


class ReviewConflict(BaseModel):
    severity: Literal["low", "medium", "high"]
    title: str
    detail: str
    related_artifact_ids: List[int] = Field(default_factory=list)


class ReviewRecommendation(BaseModel):
    label: Literal["adopt", "trial", "assess", "hold"]
    rationale: str


class TechRadarEntry(BaseModel):
    name: str
    ring: Literal["adopt", "trial", "assess", "hold"]
    quadrant: Literal["platform", "delivery", "data-ai", "experience", "architecture"]
    score: int
    evidence: str
    workspace_ids: List[int] = Field(default_factory=list)


class TechRadarRead(BaseModel):
    generated_at: datetime
    entries: List[TechRadarEntry] = Field(default_factory=list)
    counts: Dict[str, int] = Field(default_factory=dict)
    workspaces_covered: int = 0


class WorkspaceReviewRead(BaseModel):
    workspace_id: int
    generated_at: datetime
    review_input: WorkspaceReviewInput
    findings: List[ReviewFinding] = Field(default_factory=list)
    conflicts: List[ReviewConflict] = Field(default_factory=list)
    decision_summary: str
    recommendation: ReviewRecommendation
    recommended_next_steps: List[str] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)
    artifact_coverage: Dict[str, int] = Field(default_factory=dict)
    radar_entries: List[TechRadarEntry] = Field(default_factory=list)
