from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.job import JobOut

# Version allégée de JobOut pour l'inclusion dans SavedJobOut
class JobOutLite(BaseModel):
	title: Optional[str]
	company: Optional[str]
	location: Optional[str]
	url: Optional[str]
	posted_date: Optional[datetime]

	class Config:
		from_attributes = True

# Schéma pour la création d'un SavedJob
class SavedJobCreate(BaseModel):
	job_id: int

# Schéma pour la mise à jour partielle d'un SavedJob
class SavedJobUpdate(BaseModel):
	status: Optional[str] = None
	note: Optional[str] = None
	applied_at: Optional[datetime] = None
	follow_up_at: Optional[datetime] = None

# Schéma de sortie pour SavedJob, incluant les infos du job (JobOutLite)
class SavedJobOut(BaseModel):
	id: int
	job_id: int
	status: Optional[str]
	note: Optional[str]
	applied_at: Optional[datetime]
	follow_up_at: Optional[datetime]
	created_at: Optional[datetime]
	job: JobOutLite

	class Config:
		from_attributes = True
