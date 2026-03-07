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