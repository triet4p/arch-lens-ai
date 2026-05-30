import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.api import deps
from src.app.api.v1.endpoints import workspace as workspace_endpoints
from src.app.models.analysis import AnalysisResult
from src.app.models.artifact import Artifact, ArtifactStatus, ArtifactType
from src.app.models.workspace import Workspace
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.repositories.workspace import WorkspaceRepository
from src.app.services.review import WorkspaceReviewService


def create_review_test_client(session) -> tuple[TestClient, int]:
    workspace_repo = WorkspaceRepository(session)
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)

    workspace = workspace_repo.create(
        Workspace(
            name="Workspace Review API",
            constraints_json=json.dumps({"gpu_limit": "24GB VRAM", "current_stack": "Python/FastAPI"}),
        )
    )
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.REPO,
            status=ArtifactStatus.COMPLETED,
            source_url="https://github.com/acme/platform",
            metadata_json=json.dumps({"repo_id": "acme/platform"}),
        )
    )
    workspace_repo.add_artifact(workspace.id, artifact.id)
    session.add(
        AnalysisResult(
            artifact_id=artifact.id,
            analysis_kind="repository",
            extracted_data_json=json.dumps({"detected_stack": ["Python", "FastAPI"]}),
            due_diligence_score_json=json.dumps({"health_score": 86, "integration_risk": 28}),
            summary_markdown="Repository summary",
        )
    )
    session.commit()

    review_service = WorkspaceReviewService(workspace_repo, analysis_repo)

    app = FastAPI()
    app.include_router(workspace_endpoints.router, prefix="/workspaces")
    app.dependency_overrides[deps.get_workspace_review_service] = lambda: review_service

    return TestClient(app), workspace.id


def test_workspace_review_endpoints_return_review_radar_and_markdown(session):
    client, workspace_id = create_review_test_client(session)

    review_response = client.post(f"/workspaces/{workspace_id}/review")
    radar_response = client.get("/workspaces/radar")
    report_response = client.get(f"/workspaces/{workspace_id}/report.md")

    assert review_response.status_code == 200
    review_payload = review_response.json()
    assert review_payload["workspace_id"] == workspace_id
    assert review_payload["scores"]["technical_fit_score"] >= 0
    assert review_payload["recommendation"]["label"] in {"adopt", "trial", "assess", "hold"}

    assert radar_response.status_code == 200
    radar_payload = radar_response.json()
    assert radar_payload["workspaces_covered"] == 1
    assert radar_payload["entries"]

    assert report_response.status_code == 200
    assert report_response.text.startswith("# Workspace Review: Workspace Review API")


def test_workspace_review_endpoint_returns_404_for_missing_workspace(session):
    client, _workspace_id = create_review_test_client(session)

    response = client.get("/workspaces/999/review")

    assert response.status_code == 404
