## python-sidecar/src/app/api/__init__.py
```python

```

## python-sidecar/src/app/api/deps.py
```python
from __future__ import annotations
from typing import Annotated, Generator
from fastapi import Depends, Request
from sqlmodel import Session
from src.app.core.database import get_session
from src.app.repositories.workspace import WorkspaceRepository
from src.app.repositories.artifact import ArtifactRepository
from src.app.repositories.link import LinkRepository
from src.app.services.workspace import WorkspaceService
from src.app.services.ingestion import ArxivIngestor, LocalIngestor, GithubIngestor
from src.app.services.artifact import ArtifactService

# 1. Base Session Dependency
SessionDep = Annotated[Session, Depends(get_session)]

# 2. Repositories
def get_workspace_repo(session: SessionDep) -> WorkspaceRepository:
    return WorkspaceRepository(session)

def get_artifact_repo(session: SessionDep) -> ArtifactRepository:
    return ArtifactRepository(session)

def get_link_repo(session: SessionDep) -> LinkRepository:
    return LinkRepository(session)

WorkspaceRepoDep = Annotated[WorkspaceRepository, Depends(get_workspace_repo)]
ArtifactRepoDep = Annotated[ArtifactRepository, Depends(get_artifact_repo)]
LinkRepoDep = Annotated[LinkRepository, Depends(get_link_repo)]

# 3. Ingestors
def get_arxiv_ingestor(request: Request) -> ArxivIngestor:
    return ArxivIngestor(request.app.state.arxiv_api_state)

def get_local_ingestor() -> LocalIngestor:
    return LocalIngestor()

def get_github_ingestor() -> GithubIngestor:
    return GithubIngestor()

ArxivIngestorDep = Annotated[ArxivIngestor, Depends(get_arxiv_ingestor)]
LocalIngestorDep = Annotated[LocalIngestor, Depends(get_local_ingestor)]
GithubIngestorDep = Annotated[GithubIngestor, Depends(get_github_ingestor)]

# 4. Services
def get_workspace_service(
    workspace_repo: WorkspaceRepoDep,
    artifact_repo: ArtifactRepoDep
) -> WorkspaceService:
    return WorkspaceService(workspace_repo, artifact_repo)

def get_artifact_service(
    artifact_repo: ArtifactRepoDep,
    workspace_repo: WorkspaceRepoDep,
    link_repo: LinkRepoDep,
    arxiv_ingestor: ArxivIngestorDep,
    local_ingestor: LocalIngestorDep,
    github_ingestor: GithubIngestorDep
) -> ArtifactService:
    return ArtifactService(
        artifact_repo, workspace_repo, link_repo,
        arxiv_ingestor, local_ingestor, github_ingestor
    )

WorkspaceServiceDep = Annotated[WorkspaceService, Depends(get_workspace_service)]
ArtifactServiceDep = Annotated[ArtifactService, Depends(get_artifact_service)]
```

## python-sidecar/src/app/api/v1/__init__.py
```python

```

## python-sidecar/src/app/api/v1/api.py
```python
from fastapi import APIRouter
from src.app.api.v1.endpoints import health, workspace, artifact

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(workspace.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(artifact.router, prefix="/artifacts", tags=["artifacts"])
```

## python-sidecar/src/app/api/v1/endpoints/__init__.py
```python

```

## python-sidecar/src/app/api/v1/endpoints/artifact.py
```python
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from src.app.dto.artifact import ArtifactRead
from src.app.api.deps import ArtifactServiceDep

router = APIRouter()

@router.post("/arxiv/{workspace_id}", response_model=ArtifactRead)
async def add_arxiv_paper(
    workspace_id: int, 
    paper_id_or_url: str, 
    service: ArtifactServiceDep
):
    """Nạp một bài báo từ ArXiv vào Workspace"""
    try:
        return await service.add_arxiv_artifact(workspace_id, paper_id_or_url)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.post("/upload/{workspace_id}", response_model=ArtifactRead)
async def upload_local_file(
    workspace_id: int,
    file: UploadFile = File(...),
    service: ArtifactServiceDep = None
):
    """Upload một tài liệu nội bộ (PDF, DOCX, MD) vào Workspace"""
    try:
        return await service.add_local_artifact(workspace_id, file)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/github/{workspace_id}", response_model=ArtifactRead)
async def add_github_repo(
    workspace_id: int,
    repo_url: str,
    service: ArtifactServiceDep
):
    """Nạp một GitHub Repository vào Workspace"""
    try:
        return await service.add_github_artifact(workspace_id, repo_url)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub ingestion failed: {str(e)}")

# --- Delete Endpoints ---

@router.delete("/arxiv/{workspace_id}/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_arxiv_paper(
    workspace_id: int,
    artifact_id: int,
    service: ArtifactServiceDep
):
    """Xóa ArXiv Artifact: hủy liên kết, xóa PDF local và DB record"""
    deleted = await service.delete_arxiv_artifact(workspace_id, artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")

@router.delete("/upload/{workspace_id}/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_local_file(
    workspace_id: int,
    artifact_id: int,
    service: ArtifactServiceDep
):
    """Xóa Local Artifact: hủy liên kết, xóa file upload và DB record"""
    deleted = await service.delete_local_artifact(workspace_id, artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")

@router.delete("/github/{workspace_id}/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_github_repo(
    workspace_id: int,
    artifact_id: int,
    service: ArtifactServiceDep
):
    """Xóa GitHub Artifact: hủy liên kết và DB record"""
    deleted = await service.delete_github_artifact(workspace_id, artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")
```

## python-sidecar/src/app/api/v1/endpoints/health.py
```python
from fastapi import APIRouter, Request
import time

router = APIRouter()

@router.get('/')
async def hello():
    return {"status": "alive", "message": "Arch Lens AI is ready"}

@router.get("/health")
async def health_check(request: Request):
    """
    Endpoint để Frontend ping định kỳ, giữ cho Sidecar không tự tắt.
    Trả về số lượng active requests để frontend có thể quyết định skip nếu cần.
    """
    # Lấy state từ request.app (đã được khởi tạo ở main.py)
    active_requests = request.app.state.system_state.total_active_work

    # Test nhẹ các thư viện lõi
    components_status = {"status": "ok"}
    try:
        components_status = {
            "pydantic_ai": "ready",
            "markitdown": "initialized",
            "pymupdf4llm": "available",
            "sqlmodel": "ready"
        }
    except Exception as e:
        components_status = {"status": "error", "detail": str(e)}

    return {
        "status": "alive", 
        "timestamp": time.time(),
        "active_requests": active_requests,
        "busy": active_requests > 0,
        "components": components_status
    }
```

## python-sidecar/src/app/api/v1/endpoints/workspace.py
```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.app.dto.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate, WorkspaceDetail
from src.app.api.deps import WorkspaceServiceDep

router = APIRouter()

@router.get("/", response_model=List[WorkspaceRead])
async def get_workspaces(service: WorkspaceServiceDep):
    """Lấy danh sách tất cả các dự án (Dashboard)"""
    return await service.list_workspaces()

@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(dto: WorkspaceCreate, service: WorkspaceServiceDep):
    """Tạo một dự án R&D mới"""
    return await service.create_workspace(dto)

@router.get("/{workspace_id}", response_model=WorkspaceDetail)
async def get_workspace(workspace_id: int, service: WorkspaceServiceDep):
    """Lấy chi tiết một dự án và các tài liệu bên trong"""
    ws = await service.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws

@router.put("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(workspace_id: int, dto: WorkspaceUpdate, service: WorkspaceServiceDep):
    """Cập nhật thông tin dự án"""
    ws = await service.update_workspace(workspace_id, dto)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(workspace_id: int, service: WorkspaceServiceDep):
    """Xóa vĩnh viễn một dự án"""
    success = await service.delete_workspace(workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return None
```

## python-sidecar/src/app/dto/__init__.py
```python

```

## python-sidecar/src/app/dto/artifact.py
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from src.app.models.artifact import ArtifactType, ArtifactStatus

class ArtifactBase(BaseModel):
    type: ArtifactType
    source_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArtifactCreate(ArtifactBase):
    workspace_id: int

class ArtifactRead(ArtifactBase):
    id: int
    status: ArtifactStatus
    local_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

## python-sidecar/src/app/dto/common.py
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class MessageResponse(BaseModel):
    message: str
    status: str = "success"

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
```

## python-sidecar/src/app/dto/internal.py
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.app.models.artifact import ArtifactType

class IngestedArtifact(BaseModel):
    """
    Dữ liệu thô sau khi thu thập từ các nguồn (ArXiv, GitHub, v.v.)
    """
    type: ArtifactType
    source_url: str
    local_path: Optional[str] = None
    # Chứa metadata thô: {title, authors, stars, ...}
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class ProcessedContent(BaseModel):
    """
    Dữ liệu sau khi qua module Processor (ToC, Content Map)
    """
    toc: list = Field(default_factory=list)
    content_map: Dict[str, str] = Field(default_factory=dict)
    summary_markdown: Optional[str] = None
```

## python-sidecar/src/app/dto/workspace.py
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.app.dto.artifact import ArtifactRead

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    # Nhận dict từ FE, Service sẽ tự convert sang JSON string để lưu DB
    constraints: Dict[str, Any] = Field(default_factory=dict)

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None

class WorkspaceRead(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Trả về số lượng artifacts để hiển thị ở Dashboard
    artifacts_count: int = 0

    class Config:
        from_attributes = True
        
class WorkspaceDetail(WorkspaceRead):
    artifacts: List[ArtifactRead] = []

    class Config:
        from_attributes = True
```

## python-sidecar/src/app/models/__init__.py
```python
from .workspace import Workspace, WorkspaceArtifactLink
from .artifact import Artifact, ArtifactType, ArtifactStatus
from .analysis import AnalysisResult
```

## python-sidecar/src/app/models/analysis.py
```python
from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class AnalysisResult(SQLModel, table=True):
    __tablename__ = "analysis_results"

    # artifact_id đóng vai trò vừa là PK vừa là FK (Quan hệ 1-1)
    artifact_id: int = Field(
        foreign_key="artifacts.id",
        ondelete="CASCADE",
        primary_key=True
    )
    toc_json: str = Field(default="[]")
    content_map_json: str = Field(default="{}")
    summary_markdown: Optional[str] = None
    due_diligence_score_json: str = Field(default="{}")
    analyzed_at: datetime = Field(default_factory=datetime.now)

    @property
    def toc_data(self) -> list:
        try: return json.loads(self.toc_json)
        except: return []

    @property
    def content_data(self) -> Dict[str, str]:
        try: return json.loads(self.content_map_json)
        except: return {}

    @property
    def scores_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.due_diligence_score_json)
        except: return {}
```

## python-sidecar/src/app/models/artifact.py
```python
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class ArtifactType(str, Enum):
    PAPER = "paper"
    REPO = "repo"
    INTERNAL_DOC = "internal_doc"

class ArtifactStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Artifact(SQLModel, table=True):
    __tablename__ = "artifacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: ArtifactType
    status: ArtifactStatus = Field(default=ArtifactStatus.PENDING)
    source_url: str
    local_path: Optional[str] = None
    metadata_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.metadata_json)
        except: return {}
```

## python-sidecar/src/app/models/workspace.py
```python
from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlmodel import SQLModel, Field

class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    constraints_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def constraints_dict(self) -> Dict[str, Any]:
        try: return json.loads(self.constraints_json)
        except: return {}

# Bảng Link riêng biệt - Đúng chuẩn SQL
class WorkspaceArtifactLink(SQLModel, table=True):
    __tablename__ = "workspace_artifact_links"
    
    workspace_id: int = Field(
        foreign_key="workspaces.id",
        ondelete="CASCADE",
        primary_key=True
    )
    artifact_id: int = Field(
        foreign_key="artifacts.id",
        ondelete="CASCADE",
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.now)
```

## python-sidecar/src/app/repositories/__init__.py
```python

```

## python-sidecar/src/app/repositories/analysis.py
```python
from typing import Optional
from src.app.models.analysis import AnalysisResult
from src.app.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[AnalysisResult]):
    def __init__(self, session):
        super().__init__(session, AnalysisResult)

    def get_by_artifact(self, artifact_id: int) -> Optional[AnalysisResult]:
        # artifact_id là Primary Key nên dùng trực tiếp get()
        return self.get(artifact_id)
```

## python-sidecar/src/app/repositories/artifact.py
```python
from src.app.models.artifact import Artifact
from src.app.repositories.base import BaseRepository

class ArtifactRepository(BaseRepository[Artifact]):
    def __init__(self, session):
        super().__init__(session, Artifact)
```

## python-sidecar/src/app/repositories/base.py
```python
from typing import Any, Generic, TypeVar, Type, List, Optional
from sqlmodel import Session, select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get(self, id: Any) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self) -> List[T]:
        return self.session.exec(select(self.model)).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: Any) -> bool:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
```

## python-sidecar/src/app/repositories/link.py
```python
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
```

## python-sidecar/src/app/repositories/workspace.py
```python
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
```

## python-sidecar/src/app/services/__init__.py
```python

```

## python-sidecar/src/app/services/artifact.py
```python
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
        new_artifact = Artifact(
            type=ingested.type,
            status=ArtifactStatus.PENDING,
            source_url=ingested.source_url,
            local_path=ingested.local_path,
            metadata_json=json.dumps(ingested.raw_metadata)
        )
        db_artifact = self.artifact_repo.create(new_artifact)
        self.link_repo.create_link(workspace_id, db_artifact.id)
        return db_artifact

    def _to_artifact_read_dto(self, db_artifact: Artifact) -> ArtifactRead:
        """Chuyển Artifact DB object sang ArtifactRead DTO."""
        res = ArtifactRead.model_validate(db_artifact)
        res.metadata = db_artifact.metadata_dict
        return res

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
```

## python-sidecar/src/app/services/ingestion/__init__.py
```python
from ._arxiv import ArxivIngestor
from ._local import LocalIngestor
from ._github import GithubIngestor

__all__ = ["ArxivIngestor", "LocalIngestor", "GithubIngestor"]
```

## python-sidecar/src/app/services/ingestion/_arxiv.py
```python
import os
import re
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from src.app.core.constants import ARXIV_API_URL, ARXIV_XML_NAMESPACE
from src.app.core.logger import get_logger
from src.app.core.state import ArxivAPIState
from src.app.models.artifact import ArtifactType
from src.app.dto.internal import IngestedArtifact

_logger = get_logger("[Ingestion - ArXiv]")

class ArxivIngestor:
    def __init__(self, state: ArxivAPIState):
        self.state = state

    def _extract_id(self, url_or_id: str) -> str:
        """Trích xuất ArXiv ID từ URL hoặc chuỗi nhập vào"""
        pattern = r"(\d{4}\.\d{4,5}(?:v\d+)?)"
        match = re.search(pattern, url_or_id)
        return match.group(1) if match else url_or_id

    async def fetch_metadata(self, paper_id: str) -> IngestedArtifact:
        """Gọi API ArXiv để lấy metadata thô"""
        clean_id = self._extract_id(paper_id)
        params = {"id_list": clean_id}
        
        # Đảm bảo rate limit như legacy
        await self.state.wait_for_arxiv()
        
        async with httpx.AsyncClient(headers={"User-Agent": self.state.user_agent}) as client:
            resp = await client.get(ARXIV_API_URL, params=params)
            resp.raise_for_status()
            
            return self._parse_xml(resp.content, clean_id)

    def _parse_xml(self, xml_content: bytes, paper_id: str) -> IngestedArtifact:
        """Logic parse XML Atom feed từ legacy"""
        root = ET.fromstring(xml_content)
        entry = root.find('atom:entry', ARXIV_XML_NAMESPACE)
        
        if entry is None:
            raise ValueError(f"No paper found with ID: {paper_id}")

        title = entry.find('atom:title', ARXIV_XML_NAMESPACE).text.replace('\n', ' ').strip()
        summary = entry.find('atom:summary', ARXIV_XML_NAMESPACE).text.replace('\n', ' ').strip()
        authors = [a.find('atom:name', ARXIV_XML_NAMESPACE).text for a in entry.findall('atom:author', ARXIV_XML_NAMESPACE)]
        
        pdf_link = ""
        for link in entry.findall('atom:link', ARXIV_XML_NAMESPACE):
            if link.attrib.get('title') == 'pdf':
                pdf_link = link.attrib.get('href')
        
        if not pdf_link:
            pdf_link = f"https://arxiv.org/pdf/{paper_id}.pdf"

        return IngestedArtifact(
            type=ArtifactType.PAPER,
            source_url=pdf_link,
            raw_metadata={
                "paper_id": paper_id,
                "title": title,
                "authors": authors,
                "abstract": summary,
                "published": entry.find('atom:published', ARXIV_XML_NAMESPACE).text
            }
        )

    async def download_pdf(self, url: str, storage_dir: str, artifact_id: str) -> str:
        """Tải PDF về thư mục của Workspace"""
        os.makedirs(storage_dir, exist_ok=True)
        # Tạo tên file an toàn
        safe_name = re.sub(r'[^\w\-_\.]', '_', artifact_id)
        file_path = os.path.join(storage_dir, f"{safe_name}.pdf")

        _logger.info(f"⬇️ Downloading PDF: {url}")
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        
        return file_path
```

## python-sidecar/src/app/services/ingestion/_github.py
```python
import httpx
from urllib.parse import urlparse
from typing import Dict, Any
from src.app.core.logger import get_logger
from src.app.models.artifact import ArtifactType
from src.app.dto.internal import IngestedArtifact

_logger = get_logger("[Ingestion - GitHub]")

class GithubIngestor:
    def __init__(self):
        self.http_timeout = 15.0

    def _parse_url(self, url: str) -> str:
        """Trích xuất 'owner/repo' từ URL GitHub"""
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 2:
                return f"{path_parts[0]}/{path_parts[1]}"
        except Exception:
            pass
        raise ValueError(f"Invalid GitHub URL: {url}")

    async def fetch_repo_data(self, url: str) -> IngestedArtifact:
        """Thu thập metadata và cấu trúc thư mục từ GitHub API (Smart Sampling)"""
        repo_id = self._parse_url(url)
        _logger.info(f"Fetching repo data for: {repo_id}")

        async with httpx.AsyncClient(timeout=self.http_timeout) as client:
            # 1. Fetch Metadata cơ bản
            meta_resp = await client.get(f"https://api.github.com/repos/{repo_id}")
            if meta_resp.status_code != 200:
                raise ValueError(
                    f"GitHub API Error {meta_resp.status_code}. "
                    "Repo may be private or non-existent."
                )

            meta = meta_resp.json()
            default_branch = meta.get('default_branch', 'main')

            # 2. Fetch Tree Structure (Recursive) - Smart Sampling: giới hạn 200 paths
            tree_str = "Tree structure unavailable."
            tree_resp = await client.get(
                f"https://api.github.com/repos/{repo_id}/git/trees/{default_branch}?recursive=1"
            )
            if tree_resp.status_code == 200:
                tree_data = tree_resp.json().get('tree', [])
                paths = [item['path'] for item in tree_data if item['type'] in ('blob', 'tree')]
                tree_str = "\n".join(paths)

            # 3. Fetch README (Raw)
            readme_url = (
                f"https://raw.githubusercontent.com/{repo_id}/{default_branch}/README.md"
            )
            readme_resp = await client.get(readme_url, follow_redirects=True)
            readme_content = readme_resp.text if readme_resp.status_code == 200 else ""

        _logger.info(f"Successfully fetched repo data for: {repo_id}")

        return IngestedArtifact(
            type=ArtifactType.REPO,
            source_url=f"https://github.com/{repo_id}",
            raw_metadata={
                "repo_id": repo_id,
                "name": meta.get('name', ''),
                "full_name": meta.get('full_name', ''),
                "stars": meta.get('stargazers_count', 0),
                "forks": meta.get('forks_count', 0),
                "language": meta.get('language', ''),
                "description": meta.get('description', ''),
                "default_branch": default_branch,
                "tree_structure": tree_str,
                "readme_preview": readme_content,
            }
        )
```

## python-sidecar/src/app/services/ingestion/_local.py
```python
import os
import shutil
import re
from fastapi import UploadFile
from src.app.core.logger import get_logger
from src.app.models.artifact import ArtifactType
from src.app.dto.internal import IngestedArtifact

_logger = get_logger("[Ingestion - Local]")

class LocalIngestor:
    def __init__(self):
        # Các định dạng hỗ trợ (Sẽ mở rộng ở Processor phase)
        self.supported_extensions = {".pdf", ".docx", ".pptx", ".md", ".txt"}

    def _sanitize_filename(self, filename: str) -> str:
        """Làm sạch tên file để tránh path traversal và ký tự lạ"""
        name, ext = os.path.splitext(filename)
        # Chỉ giữ lại chữ cái, số, gạch ngang và gạch dưới
        clean_name = re.sub(r'[^\w\-_]', '_', name)
        return f"{clean_name}{ext.lower()}"

    async def handle_upload(self, workspace_id: int, file: UploadFile, storage_dir: str) -> IngestedArtifact:
        """Xử lý lưu file upload vào thư mục của Workspace"""
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {ext}")

        os.makedirs(storage_dir, exist_ok=True)
        
        safe_name = self._sanitize_filename(file.filename)
        # Thêm timestamp nhẹ để tránh trùng tên nếu upload nhiều lần
        file_path = os.path.join(storage_dir, safe_name)

        _logger.info(f"📁 Saving local file to: {file_path}")
        
        try:
            with open(file_path, "wb") as buffer:
                # Đọc và ghi theo chunk để tiết kiệm RAM cho file lớn
                while content := await file.read(1024 * 1024): # 1MB chunks
                    buffer.write(content)
        except Exception as e:
            _logger.error(f"Failed to save local file: {e}")
            raise e

        return IngestedArtifact(
            type=ArtifactType.INTERNAL_DOC if ext != ".pdf" else ArtifactType.PAPER,
            source_url=f"local://{safe_name}",
            local_path=file_path,
            raw_metadata={
                "original_name": file.filename,
                "file_size": os.path.getsize(file_path),
                "extension": ext
            }
        )
```

## python-sidecar/src/app/services/workspace.py
```python
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
        detail_dto.artifacts = []
        for a in db_artifacts:
            a_dto = ArtifactRead.model_validate(a)
            a_dto.metadata = a.metadata_dict # Đảm bảo metadata được giải mã từ JSON
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
```

