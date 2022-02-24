from typing import List
from pydantic import BaseModel
from datetime import datetime


class DisambiguousLinkResponse(BaseModel):
    label: str
    url: str


class SuccessResponse(BaseModel):
    data: str
    provider: str
    current_language: str
    original_language: str
    created_at: datetime


class ConflictResponse(BaseModel):
    data: List[DisambiguousLinkResponse]
    provider: str
