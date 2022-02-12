from typing import List
from pydantic import BaseModel
from datetime import datetime


class SuccessResponse(BaseModel):
    data: str
    provider: str
    current_language: str
    original_language: str
    requested_language: str
    created_at: datetime

class ConflictResponse(BaseModel):
    data: str
    provider: str