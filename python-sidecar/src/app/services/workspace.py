import json
from typing import List, Optional
from datetime import datetime
from src.app.models.workspace import Workspace
from src.app.repositories.workspace import WorkspaceRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.dto.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate, WorkspaceDetail
from src.app.dto.artifact import ArtifactRead

class WorkspaceService:
    def __init__(self, workspace_repo: WorkspaceRepository, artifact_repo: ArtifactRepository):
        self.workspace_repo = workspace_repo
        self.artifact_repo = artifact_repo

    async def list_workspaces(self) -> List[WorkspaceRead]:
        db_workspaces = self.workspace_repo.get_all()
        results = []
        for ws in db_workspaces:
            # model_validate tự động map các trường trùng tên
            read_dto = WorkspaceRead.model_validate(ws)
            # Map thủ công các trường dynamic (JSON/Property)
            read_dto.constraints = ws.constraints_dict
            read_dto.artifacts_count = self.workspace_repo.count_artifacts(ws.id)
            results.append(read_dto)
        return results

    async def get_workspace(self, workspace_id: int) -> Optional[WorkspaceDetail]:
        ws = self.workspace_repo.get(workspace_id)
        if not ws:
            return None

        # Lấy danh sách artifacts qua JOIN thủ công từ Repository
        db_artifacts = self.workspace_repo.get_artifacts(workspace_id)

        detail_dto = WorkspaceDetail.model_validate(ws)
        detail_dto.constraints = ws.constraints_dict
        detail_dto.artifacts_count = len(db_artifacts)
        
        # Map list artifact và xử lý metadata_dict cho từng cái
        # NOTE: Dùng model_dump() để tránh conflict với SQLAlchemy's built-in `metadata` attribute
        detail_dto.artifacts = []
        for a in db_artifacts:
            data = a.model_dump()
            data["metadata"] = a.metadata_dict
            a_dto = ArtifactRead.model_validate(data)
            detail_dto.artifacts.append(a_dto)
            
        return detail_dto

    async def create_workspace(self, dto: WorkspaceCreate) -> WorkspaceRead:
        new_ws = Workspace(
            name=dto.name,
            description=dto.description,
            constraints_json=json.dumps(dto.constraints),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        created_ws = self.workspace_repo.create(new_ws)
        return WorkspaceRead.model_validate(created_ws)

    async def update_workspace(self, workspace_id: int, dto: WorkspaceUpdate) -> Optional[WorkspaceRead]:
        ws = self.workspace_repo.get(workspace_id)
        if not ws:
            return None

        if dto.name is not None: ws.name = dto.name
        if dto.description is not None: ws.description = dto.description
        if dto.constraints is not None:
            ws.constraints_json = json.dumps(dto.constraints)

        ws.updated_at = datetime.now()
        updated_ws = self.workspace_repo.update(ws)
        return WorkspaceRead.model_validate(updated_ws)

    async def delete_workspace(self, workspace_id: int) -> bool:
        return self.workspace_repo.delete(workspace_id)