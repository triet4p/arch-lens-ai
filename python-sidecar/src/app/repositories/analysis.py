from typing import Optional
from src.app.models.analysis import AnalysisResult
from src.app.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[AnalysisResult]):
    def __init__(self, session):
        super().__init__(session, AnalysisResult)

    def get_by_artifact(self, artifact_id: int) -> Optional[AnalysisResult]:
        # artifact_id là Primary Key nên dùng trực tiếp get()
        return self.get(artifact_id)