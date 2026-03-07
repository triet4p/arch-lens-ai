from src.app.models.workspace import WorkspaceArtifactLink
from src.app.repositories.base import BaseRepository

class LinkRepository(BaseRepository[WorkspaceArtifactLink]):
    def __init__(self, session):
        super().__init__(session, WorkspaceArtifactLink)

    def create_link(self, workspace_id: int, artifact_id: int) -> WorkspaceArtifactLink:
        """Tạo liên kết giữa Workspace và Artifact"""
        link = WorkspaceArtifactLink(workspace_id=workspace_id, artifact_id=artifact_id)
        return self.create(link)

    def delete_link(self, workspace_id: int, artifact_id: int) -> bool:
        """Xóa liên kết giữa Workspace và Artifact (composite PK)"""
        link = self.session.get(WorkspaceArtifactLink, (workspace_id, artifact_id))
        if link:
            self.session.delete(link)
            self.session.commit()
            return True
        return False