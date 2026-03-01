import os
import sys
import inspect

if sys.stdout: sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if sys.stderr: sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)


# 1. Vô hiệu hóa Pydantic Plugin ngay lập tức
os.environ['PYDANTIC_SKIP_VALIDATOR_PLUGIN'] = '1'

# 2. Monkey patch module 'inspect' để tránh lỗi OSError: could not get source code
# Khi chạy trong file .exe, hàm này sẽ trả về chuỗi rỗng thay vì raise lỗi.
if getattr(sys, 'frozen', False):
    def patched_getsource(obj):
        return ""
    
    def patched_getsourcelines(obj):
        return ([], 0)

    inspect.getsource = patched_getsource
    inspect.getsourcelines = patched_getsourcelines
    # Patch thêm findsource nếu cần thiết cho một số bản logfire cũ
    inspect.findsource = patched_getsourcelines 
    
    
import sys
import uvicorn
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_settings import BaseSettings
import pymupdf  # PyMuPDF
import pymupdf4llm
import pymupdf.layout
from markitdown import MarkItDown
from sqlmodel import SQLModel, create_engine
import httpx

# 1. Kiểm tra Version & Imports (In ra để Tauri Log bắt được)
print(f"--- Arch Lens Sidecar Initializing ---")
print(f"Python Version: {sys.version}")
print(f"PyMuPDF Version: {pymupdf.__version__}")
print(f"FastAPI Version: {FastAPI.__module__}")

# 2. Cấu hình Settings đơn giản
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Arch Lens AI Backend"

settings = Settings()

# 3. Khởi tạo FastAPI
app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
async def root():
    return {"message": "Arch Lens Sidecar is running"}

@app.get("/health")
async def health_check():
    # Test thử một instance PydanticAI Agent (chưa cần gọi LLM)
    test_agent = Agent('openai:gpt-4o', system_prompt="Health check")
    
    # Test thử MarkItDown
    md = MarkItDown()
    
    return {
        "status": "ok",
        "components": {
            "pydantic_ai": "initialized",
            "markitdown": "initialized",
            "pymupdf": "available",
            "sqlmodel": "ready"
        }
    }

if __name__ == "__main__":
    print(f"🚀 Sidecar starting on http://127.0.0.1:14201")
    uvicorn.run(app, host="127.0.0.1", port=14201, log_level="info")