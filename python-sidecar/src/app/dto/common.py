from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class MessageResponse(BaseModel):
    message: str
    status: str = "success"

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int