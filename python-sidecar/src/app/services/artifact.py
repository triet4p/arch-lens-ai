import json
import os

from fastapi import UploadFile
from src.app.core.config import settings
from src.app.core.logger import get_logger
from src.app.repositories.artifact import ArtifactRepository
from src.app.repositories.workspace import WorkspaceRepository
from src.app.repositories.link import LinkRepository # Thêm Junction Repo
from src.app.models.artifact import Artifact, ArtifactStatus
from src.app.services.ingestion import ArxivIngestor, LocalIngestor, GithubIngestor
from src.app.dto.artifact import ArtifactRead

_logger = get_logger("[Service - Artifact]")

class ArtifactService:
    def __init__(
        self,
        artifact_repo: ArtifactRepository,
        workspace_repo: WorkspaceRepository,
        link_repo: LinkRepository,
        arxiv_ingestor: ArxivIngestor,
        local_ingestor: LocalIngestor,
        github_ingestor: GithubIngestor
    ):
        self.artifact_repo = artifact_repo
        self.workspace_repo = workspace_repo
        self.link_repo = link_repo
        self.arxiv_ingestor = arxiv_ingestor
        self.local_ingestor = local_ingestor
        self.github_ingestor = github_ingestor

    # --- Private Helpers ---

    def _create_and_link(self, workspace_id: int, ingested) -> Artifact:
        """Tạo Artifact record và tạo liên kết Workspace - dùng chung cho mọi ingestor."""
        _logger.debug(f"Creating artifact record for {ingested.name if hasattr(ingested, 'name') else 'unknown'} (type: {ingested.type})")
        new_artifact = Artifact(
            name=ingested.name if hasattr(ingested, 'name') else "Unnamed",
            type=ingested.type,
            status=ArtifactStatus.PENDING,
            source_url=ingested.source_url,
            local_path=ingested.local_path,
            metadata_json=json.dumps(ingested.raw_metadata)
        )
        _logger.debug(f"Saving artifact to DB...")
        db_artifact = self.artifact_repo.create(new_artifact)
        _logger.debug(f"Artifact saved with ID: {db_artifact.id}. Linking to workspace {workspace_id}...")
        self.link_repo.create_link(workspace_id, db_artifact.id)
        _logger.debug(f"Link created successfully.")
        return db_artifact

    def _to_artifact_read_dto(self, db_artifact: Artifact) -> ArtifactRead:
        """Chuyển Artifact DB object sang ArtifactRead DTO."""
        _logger.debug(f"Converting artifact {db_artifact.id} to DTO...")
        # NOTE: Dùng model_dump() để tránh conflict với SQLAlchemy's built-in `metadata` attribute
        # (MetaData() registry object) khi dùng model_validate trực tiếp lên SQLModel instance.
        data = db_artifact.model_dump()
        data["metadata"] = db_artifact.metadata_dict
        return ArtifactRead.model_validate(data)

    # --- Public Methods ---

    async def add_arxiv_artifact(self, workspace_id: int, paper_id_or_url: str) -> ArtifactRead:
        """
        Luồng nạp ArXiv Paper: Ingest -> Save DB -> Link Workspace (Sử dụng Repositories)
        """
        # 1. Kiểm tra Workspace tồn tại
        if not self.workspace_repo.get(workspace_id):
            raise ValueError(f"Workspace {workspace_id} not found")

        # 2. Fetch Metadata từ Ingestor
        ingested = await self.arxiv_ingestor.fetch_metadata(paper_id_or_url)

        # 3. Tạo record + liên kết
        db_artifact = self._create_and_link(workspace_id, ingested)

        # 4. Download PDF (arxiv-specific)
        workspace_path = os.path.join(settings.WORKSPACE_STORAGE_DIR, str(workspace_id), "artifacts")
        try:
            local_path = await self.arxiv_ingestor.download_pdf(
                ingested.source_url,
                workspace_path,
                f"paper_{db_artifact.id}"
            )
            db_artifact.local_path = local_path
            self.artifact_repo.update(db_artifact)
        except Exception as e:
            _logger.error(f"Failed to download PDF: {e}")
            db_artifact.status = ArtifactStatus.FAILED
            self.artifact_repo.update(db_artifact)
            raise e

        return self._to_artifact_read_dto(db_artifact)

    async def add_local_artifact(self, workspace_id: int, file: UploadFile) -> ArtifactRead:
        """
        Luồng nạp File nội bộ: Upload -> Save to Workspace Dir -> DB Record -> Link
        """
        # 1. Kiểm tra Workspace
        if not self.workspace_repo.get(workspace_id):
            raise ValueError(f"Workspace {workspace_id} not found")

        # 2. Ingest file vật lý
        workspace_path = os.path.join(settings.WORKSPACE_STORAGE_DIR, str(workspace_id), "artifacts")
        ingested = await self.local_ingestor.handle_upload(workspace_id, file, workspace_path)

        # 3. Tạo record + liên kết
        db_artifact = self._create_and_link(workspace_id, ingested)
        return self._to_artifact_read_dto(db_artifact)

    async def add_github_artifact(self, workspace_id: int, repo_url: str) -> ArtifactRead:
        """Luồng nạp GitHub Repo: Fetch Metadata -> DB Record -> Link"""
        if not self.workspace_repo.get(workspace_id):
            raise ValueError(f"Workspace {workspace_id} not found")

        # 1. Ingest metadata từ GitHub API
        ingested = await self.github_ingestor.fetch_repo_data(repo_url)

        # 2. Tạo record + liên kết
        db_artifact = self._create_and_link(workspace_id, ingested)
        return self._to_artifact_read_dto(db_artifact)

    # --- Delete Methods ---

    def _delete_artifact_record(self, workspace_id: int, artifact_id: int) -> None:
        """Xóa liên kết Workspace-Artifact rồi xóa Artifact record."""
        self.link_repo.delete_link(workspace_id, artifact_id)
        self.artifact_repo.delete(artifact_id)

    async def delete_arxiv_artifact(self, workspace_id: int, artifact_id: int) -> bool:
        """Xóa ArXiv Artifact: hủy liên kết + xóa PDF local + xóa DB record."""
        artifact = self.artifact_repo.get(artifact_id)
        if not artifact:
            return False

        # Xóa file PDF vật lý nếu tồn tại
        if artifact.local_path and os.path.exists(artifact.local_path):
            try:
                os.remove(artifact.local_path)
            except Exception as e:
                _logger.warning(f"Failed to delete PDF file {artifact.local_path}: {e}")

        self._delete_artifact_record(workspace_id, artifact_id)
        return True

    async def delete_local_artifact(self, workspace_id: int, artifact_id: int) -> bool:
        """Xóa Local Artifact: hủy liên kết + xóa file upload local + xóa DB record."""
        artifact = self.artifact_repo.get(artifact_id)
        if not artifact:
            return False

        # Xóa file upload vật lý nếu tồn tại
        if artifact.local_path and os.path.exists(artifact.local_path):
            try:
                os.remove(artifact.local_path)
            except Exception as e:
                _logger.warning(f"Failed to delete uploaded file {artifact.local_path}: {e}")

        self._delete_artifact_record(workspace_id, artifact_id)
        return True

    async def delete_github_artifact(self, workspace_id: int, artifact_id: int) -> bool:
        """Xóa GitHub Artifact: hủy liên kết + xóa DB record (không có file local)."""
        if not self.artifact_repo.get(artifact_id):
            return False

        self._delete_artifact_record(workspace_id, artifact_id)
        return True
