from typing import Optional

from sqlmodel import select

from src.app.models.analysis import AnalysisResult
from src.app.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[AnalysisResult]):
    def __init__(self, session):
        super().__init__(session, AnalysisResult)

    def get_by_artifact(self, artifact_id: int) -> Optional[AnalysisResult]:
        return self.get(artifact_id)

    def list_by_artifact_ids(self, artifact_ids: list[int]) -> dict[int, AnalysisResult]:
        if not artifact_ids:
            return {}

        statement = select(AnalysisResult).where(AnalysisResult.artifact_id.in_(artifact_ids))
        records = self.session.exec(statement).all()
        return {record.artifact_id: record for record in records}

    def upsert_for_artifact(self, result: AnalysisResult) -> AnalysisResult:
        existing = self.get_by_artifact(result.artifact_id)
        if existing:
            existing.analysis_kind = result.analysis_kind
            existing.toc_json = result.toc_json
            existing.content_map_json = result.content_map_json
            existing.extracted_data_json = result.extracted_data_json
            existing.summary_markdown = result.summary_markdown
            existing.due_diligence_score_json = result.due_diligence_score_json
            existing.analyzed_at = result.analyzed_at
            return self.update(existing)

        return self.create(result)
