import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from src.app.models.artifact import Artifact, ArtifactStatus, ArtifactType
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.services.analysis import AnalysisService


def test_analyze_local_document_persists_summary(session, tmp_path: Path):
    document_path = tmp_path / "strategy.md"
    document_path.write_text(
        "# Architecture Review\n\n"
        "## Goals\n\nValidate local markdown parsing.\n\n"
        "## Constraints\n\nGPU budget is limited.\n",
        encoding="utf-8",
    )

    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.INTERNAL_DOC,
            status=ArtifactStatus.PENDING,
            source_url="local://strategy.md",
            local_path=str(document_path),
            metadata_json=json.dumps({"original_name": "strategy.md", "extension": ".md"}),
        )
    )

    service = AnalysisService(artifact_repo, analysis_repo)
    result = asyncio.run(service.analyze_artifact(artifact.id))

    stored_artifact = artifact_repo.get(artifact.id)
    stored_analysis = analysis_repo.get_by_artifact(artifact.id)

    assert result.analysis_kind == "document"
    assert result.extracted_data["headings_count"] == 3
    assert "Architecture Review" in result.summary_markdown
    assert stored_artifact.status == ArtifactStatus.COMPLETED
    assert stored_analysis is not None
    assert stored_analysis.analysis_kind == "document"


def test_markdown_analysis_does_not_require_markitdown_runtime(session, tmp_path: Path):
    document_path = tmp_path / "notes.md"
    document_path.write_text("# Notes\n\nLocal markdown path.\n", encoding="utf-8")

    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.INTERNAL_DOC,
            status=ArtifactStatus.PENDING,
            source_url="local://notes.md",
            local_path=str(document_path),
            metadata_json=json.dumps({"original_name": "notes.md", "extension": ".md"}),
        )
    )

    service = AnalysisService(artifact_repo, analysis_repo)
    with patch("src.app.services.analysis.MarkItDown", side_effect=RuntimeError("should not be called")):
        result = asyncio.run(service.analyze_artifact(artifact.id))

    assert result.analysis_kind == "document"
    assert "Notes" in result.summary_markdown


def test_analyze_repository_derives_stack_and_scores(session):
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.REPO,
            status=ArtifactStatus.PENDING,
            source_url="https://github.com/acme/platform",
            metadata_json=json.dumps(
                {
                    "repo_id": "acme/platform",
                    "full_name": "acme/platform",
                    "language": "Python",
                    "stars": 120,
                    "forks": 15,
                    "default_branch": "main",
                    "tree_structure": "frontend/package.json\nfrontend/src/App.tsx\npython-sidecar/pyproject.toml\nsrc-tauri/Cargo.toml",
                    "readme_preview": "Built with React, Tauri, and FastAPI.",
                }
            ),
        )
    )

    service = AnalysisService(artifact_repo, analysis_repo)
    result = asyncio.run(service.analyze_artifact(artifact.id))

    assert result.analysis_kind == "repository"
    assert "React" in result.extracted_data["detected_stack"]
    assert "health_score" in result.scores
    assert result.scores["integration_risk"] >= 0


def test_analyze_arxiv_uses_metadata_when_pdf_is_missing(session):
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.PAPER,
            status=ArtifactStatus.PENDING,
            source_url="https://arxiv.org/pdf/2401.00001.pdf",
            metadata_json=json.dumps(
                {
                    "paper_id": "2401.00001",
                    "title": "Efficient Local Reasoning",
                    "authors": ["Jane Doe", "John Roe"],
                    "abstract": "We evaluate GPU tradeoffs and implementation details for local reasoning systems.",
                    "published": "2026-01-10T00:00:00Z",
                }
            ),
        )
    )

    service = AnalysisService(artifact_repo, analysis_repo)
    result = asyncio.run(service.analyze_artifact(artifact.id))

    assert result.analysis_kind == "paper"
    assert result.extracted_data["paper_id"] == "2401.00001"
    assert result.scores["implementation_signal"] > 0
    assert "Efficient Local Reasoning" in result.summary_markdown
