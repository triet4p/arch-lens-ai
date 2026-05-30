from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse

from src.app.dto.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate, WorkspaceDetail
from src.app.dto.review import TechRadarRead, WorkspaceReviewRead
from src.app.api.deps import WorkspaceReviewServiceDep, WorkspaceServiceDep

router = APIRouter()

@router.get("/", response_model=List[WorkspaceRead])
async def get_workspaces(service: WorkspaceServiceDep):
    """Lấy danh sách tất cả các dự án (Dashboard)"""
    return await service.list_workspaces()

@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(dto: WorkspaceCreate, service: WorkspaceServiceDep):
    """Tạo một dự án R&D mới"""
    return await service.create_workspace(dto)

@router.get("/radar", response_model=TechRadarRead)
async def get_tech_radar(service: WorkspaceReviewServiceDep):
    """Tổng hợp tín hiệu Tech Radar across workspace reviews."""
    return await service.get_tech_radar()

@router.get("/{workspace_id}", response_model=WorkspaceDetail)
async def get_workspace(workspace_id: int, service: WorkspaceServiceDep):
    """Lấy chi tiết một dự án và các tài liệu bên trong"""
    ws = await service.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws

@router.get("/{workspace_id}/review", response_model=WorkspaceReviewRead)
async def get_workspace_review(workspace_id: int, service: WorkspaceReviewServiceDep):
    """Lấy workspace-level review dựa trên constraint và analysis records hiện có."""
    try:
        return await service.get_workspace_review(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@router.post("/{workspace_id}/review", response_model=WorkspaceReviewRead)
async def run_workspace_review(workspace_id: int, service: WorkspaceReviewServiceDep):
    """Chạy cross-verification cho một workspace."""
    try:
        return await service.get_workspace_review(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@router.get("/{workspace_id}/report.md", response_class=PlainTextResponse)
async def export_workspace_report(workspace_id: int, service: WorkspaceReviewServiceDep):
    """Xuất workspace review thành markdown report."""
    try:
        return await service.export_workspace_report(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

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
