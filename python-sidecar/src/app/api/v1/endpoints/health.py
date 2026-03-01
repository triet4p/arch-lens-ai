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