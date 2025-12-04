from pydantic import BaseModel
from datetime import datetime


class JobOut(BaseModel):
    id: int
    job_id: str | None
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
    items: list[JobOut]
    total: int