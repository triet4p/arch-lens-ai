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