from pydantic import BaseModel
from datetime import datetime
from typing import List

class JobOut(BaseModel):
    id: int
    jobId: str | int | None
    title: str | None
    company: str | None
    location: str | None
    url: str | None
    contract_type: str | None
    posted_date: datetime | None
    active: bool | None


class Config:
    from_attributes = True # Pydantic v2: lit directement les ORM objects


class JobsResponse(BaseModel):
    items: List[JobOut]
    total: int
    page: int
    page_size: int
    total_pages: int