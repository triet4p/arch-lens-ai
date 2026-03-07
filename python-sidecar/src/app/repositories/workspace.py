from typing import List
from sqlmodel import select, func
from src.app.models.workspace import Workspace, WorkspaceArtifactLink
from src.app.models.artifact import Artifact
from src.app.repositories.base import BaseRepository

class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session):
        super().__init__(session, Workspace)

    def get_artifacts(self, workspace_id: int) -> List[Artifact]:
        statement = (
            select(Artifact)
            .join(WorkspaceArtifactLink, WorkspaceArtifactLink.artifact_id == Artifact.id)
            .where(WorkspaceArtifactLink.workspace_id == workspace_id)
        )
        return self.session.exec(statement).all()

    def count_artifacts(self, workspace_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(WorkspaceArtifactLink)
            .where(WorkspaceArtifactLink.workspace_id == workspace_id)
        )
        return self.session.exec(statement).one()

    def add_artifact(self, workspace_id: int, artifact_id: int) -> WorkspaceArtifactLink:
        link = WorkspaceArtifactLink(workspace_id=workspace_id, artifact_id=artifact_id)
        self.session.add(link)
        self.session.commit()
        return link

    def remove_artifact(self, workspace_id: int, artifact_id: int) -> bool:
        link = self.session.get(WorkspaceArtifactLink, (workspace_id, artifact_id))
        if link:
            self.session.delete(link)
            self.session.commit()
            return True
        return False