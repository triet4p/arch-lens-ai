from fastapi import APIRouter, File, HTTPException, UploadFile, status
from src.app.dto.artifact import ArtifactRead
from src.app.api.deps import ArtifactServiceDep
from src.app.core.logger import get_logger

_logger = get_logger("[API - Artifact]")

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
    service: ArtifactServiceDep,
    file: UploadFile = File(...),
):
    """Upload một tài liệu nội bộ (PDF, DOCX, MD) vào Workspace"""
    try:
        _logger.debug(f"Handling upload request for workspace: {workspace_id}, file: {file.filename}")
        return await service.add_local_artifact(workspace_id, file)
    except ValueError as ve:
        _logger.error(f"Upload ValueError for workspace {workspace_id}: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        _logger.error(f"CRITICAL: Upload unexpected error for workspace {workspace_id}: {e}", exc_info=True)
        # Tạm thời trả về lỗi chi tiết để debug
        raise HTTPException(status_code=500, detail=f"DEBUG ERROR: {type(e).__name__} - {str(e)}")

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