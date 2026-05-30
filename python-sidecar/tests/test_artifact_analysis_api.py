from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.api import deps
from src.app.api.v1.endpoints import artifact as artifact_endpoints
from src.app.dto.analysis import AnalysisRead


class StubAnalysisService:
    async def analyze_artifact(self, artifact_id: int) -> AnalysisRead:
        return AnalysisRead.model_validate(
            {
                "artifact_id": artifact_id,
                "analysis_kind": "document",
                "summary_markdown": "Synthetic summary",
                "extracted_data": {"title": "Synthetic"},
                "scores": {"structure_score": 80},
                "toc": [],
                "content_map": {},
                "analyzed_at": "2026-05-30T00:00:00",
            }
        )

    async def get_analysis(self, artifact_id: int):
        if artifact_id == 404:
            return None
        return await self.analyze_artifact(artifact_id)


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(artifact_endpoints.router, prefix="/artifacts")
    app.dependency_overrides[deps.get_analysis_service] = lambda: StubAnalysisService()
    return TestClient(app)


def test_analyze_endpoint_returns_analysis_payload():
    client = create_test_client()

    response = client.post("/artifacts/7/analyze")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_id"] == 7
    assert payload["analysis_kind"] == "document"
    assert payload["scores"]["structure_score"] == 80


def test_get_analysis_endpoint_returns_404_when_missing():
    client = create_test_client()

    response = client.get("/artifacts/404/analysis")

    assert response.status_code == 404
