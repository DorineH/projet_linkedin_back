import html
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobLeaddev
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.db.models import UserSavedJob, JobLeaddev
from app.schemas.saved_job import SavedJobCreate, SavedJobUpdate, SavedJobOut, JobOutLite
from sqlalchemy import update, delete

async def search_jobs(
    session: AsyncSession,
    q: Optional[str] = None,
    company: Optional[str] = None,
    contract_type: Optional[str] = None,
    active: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort: str = "-posted_date",
    limit: int = 20,
    offset: int = 0,
):
    """Recherche simple dans jobs_leaddev avec filtres + tri + pagination."""

    conditions = []

    if active is not None:
        conditions.append(JobLeaddev.active == active)

    if company:
        conditions.append(JobLeaddev.company.ilike(f"%{company}%"))

    if contract_type:
        conditions.append(JobLeaddev.contract_type == contract_type)

    if date_from:
        conditions.append(JobLeaddev.posted_date >= text(f"'{date_from}'"))

    if date_to:
        conditions.append(JobLeaddev.posted_date <= text(f"'{date_to}'"))

    if q:
        like = f"%{q}%"
        conditions.append(
            or_(
                JobLeaddev.title.ilike(like),
                JobLeaddev.company.ilike(like),
                JobLeaddev.location.ilike(like),
                JobLeaddev.description.ilike(like),
            )
        )

    stmt = select(JobLeaddev)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    if sort.startswith("-"):
        colname = sort[1:]
        col = getattr(JobLeaddev, colname, JobLeaddev.posted_date)
        stmt = stmt.order_by(col.desc())
    else:
        colname = sort
        col = getattr(JobLeaddev, colname, JobLeaddev.posted_date)
        stmt = stmt.order_by(col.asc())

    # Pagination
    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    items = result.scalars().all()

    for job in items:
        if hasattr(job, 'title') and job.title:
            job.title = html.unescape(job.title)
        if hasattr(job, 'company') and job.company:
            job.company = html.unescape(job.company)
        if hasattr(job, 'location') and job.location:
            job.location = html.unescape(job.location)
        if hasattr(job, 'url') and job.url:
            job.url = html.unescape(job.url)

    if conditions:
        subq = select(JobLeaddev).where(and_(*conditions)).subquery()
        count_stmt = select(func.count()).select_from(subq)
    else:
        count_stmt = select(func.count()).select_from(JobLeaddev)

    result = await session.execute(count_stmt)
    total = result.scalar_one()
    return items, total

# Save job offer for a user
async def save_job(session: AsyncSession, user_id: UUID, job_id: int):
    job = await session.get(JobLeaddev, job_id)
    if not job:
        return None

    stmt = select(UserSavedJob).where(UserSavedJob.user_id == user_id, UserSavedJob.job_id == job_id)
    result = await session.execute(stmt)
    saved = result.scalar_one_or_none()
    if saved:
        return saved

    new_saved = UserSavedJob(user_id=user_id, job_id=job_id)
    session.add(new_saved)
    await session.commit()
    await session.refresh(new_saved)
    return new_saved

# List saved job offers for a user with optional filters and pagination
async def list_saved_jobs(session: AsyncSession, user_id: UUID, status: Optional[str], q: Optional[str], page: int = 1, page_size: int = 20):
    conditions = [UserSavedJob.user_id == user_id]
    if status:
        conditions.append(UserSavedJob.status == status)
    if q:
        like = f"%{q}%"
        conditions.append(
            or_(JobLeaddev.title.ilike(like), JobLeaddev.company.ilike(like), JobLeaddev.location.ilike(like))
        )

    count_stmt = (
        select(func.count())
        .select_from(UserSavedJob)
        .join(JobLeaddev, UserSavedJob.job_id == JobLeaddev.id)
        .where(and_(*conditions))
    )
    result = await session.execute(count_stmt)
    total = result.scalar_one()

    stmt = (
        select(UserSavedJob, JobLeaddev)
        .join(JobLeaddev, UserSavedJob.job_id == JobLeaddev.id)
        .where(and_(*conditions))
        .order_by(UserSavedJob.id.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    result = await session.execute(stmt)
    items = []
    for saved, job in result.all():
        if hasattr(job, 'title') and job.title:
            job.title = html.unescape(job.title)
        if hasattr(job, 'company') and job.company:
            job.company = html.unescape(job.company)
        if hasattr(job, 'location') and job.location:
            job.location = html.unescape(job.location)
        if hasattr(job, 'url') and job.url:
            job.url = html.unescape(job.url)
        job_lite = JobOutLite.model_validate(job)
        items.append(SavedJobOut(
            id=saved.id,
            job_id=saved.job_id,
            status=getattr(saved, 'status', None),
            note=getattr(saved, 'note', None),
            applied_at=getattr(saved, 'applied_at', None),
            follow_up_at=getattr(saved, 'follow_up_at', None),
            created_at=getattr(saved, 'created_at', None),
            job=job_lite
        ))
    return {"items": items, "total": total, "page": page, "page_size": page_size}

# Update a saved job
async def update_saved_job(session: AsyncSession, user_id: UUID, saved_id: int, payload: SavedJobUpdate):
    stmt = select(UserSavedJob).where(UserSavedJob.id == saved_id, UserSavedJob.user_id == user_id)
    result = await session.execute(stmt)
    saved = result.scalar_one_or_none()
    if not saved:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(saved, field, value)
    await session.commit()
    await session.refresh(saved)
    return saved

# Delete a saved job
async def delete_saved_job(session: AsyncSession, user_id: UUID, saved_id: int):
    stmt = select(UserSavedJob).where(UserSavedJob.id == saved_id, UserSavedJob.user_id == user_id)
    result = await session.execute(stmt)
    saved = result.scalar_one_or_none()
    if not saved:
        return False
    await session.delete(saved)
    await session.commit()
    return True

# Get the list of saved job IDs for a user
async def get_saved_job_ids(session: AsyncSession, user_id: UUID):
    stmt = select(UserSavedJob.job_id).where(UserSavedJob.user_id == user_id)
    result = await session.execute(stmt)
    return [row[0] for row in result.all()]
