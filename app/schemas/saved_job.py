from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.job import JobOut

class JobOutLite(BaseModel):
	model_config = {"from_attributes": True}

	title: Optional[str] = None
	company: Optional[str] = None
	location: Optional[str] = None
	url: Optional[str] = None
	posted_date: Optional[datetime] = None

class SavedJobCreate(BaseModel):
	job_id: int

class SavedJobUpdate(BaseModel):
	status: Optional[str] = None
	note: Optional[str] = None
	applied_at: Optional[datetime] = None
	follow_up_at: Optional[datetime] = None

class SavedJobOut(BaseModel):
	model_config = {"from_attributes": True}

	id: int
	job_id: int
	status: Optional[str] = None
	note: Optional[str] = None
	applied_at: Optional[datetime] = None
	follow_up_at: Optional[datetime] = None
	created_at: Optional[datetime] = None
	job: Optional[JobOutLite] = None
