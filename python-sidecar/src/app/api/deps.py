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