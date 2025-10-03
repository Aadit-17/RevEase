from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReviewBase(BaseModel):
    location: str
    rating: int
    text: str
    date: datetime
    topic: Optional[str] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class ReviewCreate(ReviewBase):
    session_id: UUID

class Review(ReviewBase):
    id: int
    session_id: UUID
    sentiment: Optional[str] = None
    topic: Optional[str] = None
    reply: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }