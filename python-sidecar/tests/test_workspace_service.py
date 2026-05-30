import asyncio
import json
from pathlib import Path

from src.app.models.analysis import AnalysisResult
from src.app.models.artifact import Artifact, ArtifactStatus, ArtifactType
from src.app.models.workspace import Workspace, WorkspaceArtifactLink
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.repositories.workspace import WorkspaceRepository
from src.app.services.workspace import WorkspaceService


def test_delete_workspace_removes_links_artifacts_analysis_and_files(session, tmp_path: Path):
    file_path = tmp_path / "draft.md"
    file_path.write_text("# Draft\n\ncontent\n", encoding="utf-8")

    workspace_repo = WorkspaceRepository(session)
    artifact_repo = ArtifactRepository(session)
    analysis_repo = AnalysisRepository(session)
    service = WorkspaceService(workspace_repo, artifact_repo, analysis_repo)

    workspace = workspace_repo.create(
        Workspace(name="test", description="temp", constraints_json=json.dumps({}))
    )
    artifact = artifact_repo.create(
        Artifact(
            type=ArtifactType.INTERNAL_DOC,
            status=ArtifactStatus.COMPLETED,
            source_url="local://draft.md",
            local_path=str(file_path),
            metadata_json=json.dumps({"original_name": "draft.md", "extension": ".md"}),
        )
    )
    session.add(WorkspaceArtifactLink(workspace_id=workspace.id, artifact_id=artifact.id))
    session.add(
        AnalysisResult(
            artifact_id=artifact.id,
            analysis_kind="document",
            summary_markdown="done",
        )
    )
    session.commit()

    deleted = asyncio.run(service.delete_workspace(workspace.id))

    assert deleted is True
    assert workspace_repo.get(workspace.id) is None
    assert artifact_repo.get(artifact.id) is None
    assert analysis_repo.get_by_artifact(artifact.id) is None
    assert not file_path.exists()
    assert workspace_repo.count_artifacts(workspace.id) == 0
