import asyncio
import json

from src.app.models.analysis import AnalysisResult
from src.app.models.artifact import Artifact, ArtifactStatus, ArtifactType
from src.app.models.workspace import Workspace
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.repositories.workspace import WorkspaceRepository
from src.app.services.review import WorkspaceReviewService


def test_workspace_review_builds_findings_conflicts_and_radar(session):
    workspace_repo = WorkspaceRepository(session)
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)

    workspace = workspace_repo.create(
        Workspace(
            name="Agent Evaluation",
            description="Compare local-first stacks for technical due diligence.",
            constraints_json=json.dumps({"gpu_limit": "16GB VRAM", "current_stack": "Python/FastAPI"}),
        )
    )

    repo_artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.REPO,
            status=ArtifactStatus.COMPLETED,
            source_url="https://github.com/acme/agent-stack",
            metadata_json=json.dumps({"repo_id": "acme/agent-stack"}),
        )
    )
    doc_artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.INTERNAL_DOC,
            status=ArtifactStatus.COMPLETED,
            source_url="local://architecture.md",
            metadata_json=json.dumps({"original_name": "architecture.md"}),
        )
    )
    paper_artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.PAPER,
            status=ArtifactStatus.COMPLETED,
            source_url="https://arxiv.org/pdf/2601.00001.pdf",
            metadata_json=json.dumps({"title": "Local Agentic Reasoning"}),
        )
    )
    pending_artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.INTERNAL_DOC,
            status=ArtifactStatus.PENDING,
            source_url="local://backlog.md",
            metadata_json=json.dumps({"original_name": "backlog.md"}),
        )
    )

    for artifact in (repo_artifact, doc_artifact, paper_artifact, pending_artifact):
        workspace_repo.add_artifact(workspace.id, artifact.id)

    session.add(
        AnalysisResult(
            artifact_id=repo_artifact.id,
            analysis_kind="repository",
            extracted_data_json=json.dumps({"detected_stack": ["Python", "FastAPI", "PyTorch"]}),
            due_diligence_score_json=json.dumps({"health_score": 82, "complexity_score": 48, "integration_risk": 72}),
            summary_markdown="Repository summary",
        )
    )
    session.add(
        AnalysisResult(
            artifact_id=doc_artifact.id,
            analysis_kind="document",
            extracted_data_json=json.dumps({"title": "Architecture Review"}),
            due_diligence_score_json=json.dumps({"readiness_score": 74, "structure_score": 86}),
            summary_markdown="Internal architecture review",
        )
    )
    session.add(
        AnalysisResult(
            artifact_id=paper_artifact.id,
            analysis_kind="paper",
            extracted_data_json=json.dumps({"title": "Local Agentic Reasoning"}),
            due_diligence_score_json=json.dumps({"implementation_signal": 68, "reproducibility_signal": 62}),
            summary_markdown="Paper summary",
        )
    )
    session.commit()

    service = WorkspaceReviewService(workspace_repo, analysis_repo)

    review = asyncio.run(service.get_workspace_review(workspace.id))
    report = asyncio.run(service.export_workspace_report(workspace.id))

    assert review.review_input.workspace_name == "Agent Evaluation"
    assert review.artifact_coverage["analyzed_artifacts"] == 3
    assert review.artifact_coverage["pending_artifacts"] == 1
    assert review.findings
    assert review.conflicts
    assert any(conflict.title == "GPU ceiling may limit ML adoption" for conflict in review.conflicts)
    assert any(entry.name == "FastAPI" for entry in review.radar_entries)
    assert review.recommendation.label in {"hold", "assess", "trial", "adopt"}
    assert "# Workspace Review: Agent Evaluation" in report
    assert "## Tech Radar Signals" in report


def test_workspace_tech_radar_aggregates_across_reviews(session):
    workspace_repo = WorkspaceRepository(session)
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)

    first_workspace = workspace_repo.create(
        Workspace(name="First", constraints_json=json.dumps({"current_stack": "React/Tauri"}))
    )
    second_workspace = workspace_repo.create(
        Workspace(name="Second", constraints_json=json.dumps({"current_stack": "Python/FastAPI"}))
    )

    first_repo = artifact_repo.create(
        Artifact(
            type=ArtifactType.REPO,
            status=ArtifactStatus.COMPLETED,
            source_url="https://github.com/acme/desktop",
            metadata_json=json.dumps({"repo_id": "acme/desktop"}),
        )
    )
    second_repo = artifact_repo.create(
        Artifact(
            type=ArtifactType.REPO,
            status=ArtifactStatus.COMPLETED,
            source_url="https://github.com/acme/api",
            metadata_json=json.dumps({"repo_id": "acme/api"}),
        )
    )

    workspace_repo.add_artifact(first_workspace.id, first_repo.id)
    workspace_repo.add_artifact(second_workspace.id, second_repo.id)

    session.add(
        AnalysisResult(
            artifact_id=first_repo.id,
            analysis_kind="repository",
            extracted_data_json=json.dumps({"detected_stack": ["React", "Tauri"]}),
            due_diligence_score_json=json.dumps({"health_score": 84, "integration_risk": 34}),
            summary_markdown="Desktop stack",
        )
    )
    session.add(
        AnalysisResult(
            artifact_id=second_repo.id,
            analysis_kind="repository",
            extracted_data_json=json.dumps({"detected_stack": ["Python", "FastAPI"]}),
            due_diligence_score_json=json.dumps({"health_score": 78, "integration_risk": 38}),
            summary_markdown="Backend stack",
        )
    )
    session.commit()

    service = WorkspaceReviewService(workspace_repo, analysis_repo)
    radar = asyncio.run(service.get_tech_radar())

    assert radar.workspaces_covered == 2
    assert radar.entries
    assert any(entry.name in {"React", "Python"} for entry in radar.entries)
