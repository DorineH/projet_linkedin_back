import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import UUID, select, text
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import JobLeaddev
from app.db.session import get_session
from app.schemas.job import JobOut, JobsResponse
from app.services.job_service import search_jobs
from fastapi import Body
from app.schemas.saved_job import SavedJobCreate, SavedJobUpdate, SavedJobOut
from app.services.job_service import save_job, list_saved_jobs, update_saved_job, delete_saved_job, get_saved_job_ids


router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/jobs", response_model=JobsResponse)
async def list_jobs(
    q: str | None = Query(default=None, description="Recherche texte (simple)"),
    company: str | None = None,
    contract_type: str | None = None,
    active: bool | None = None,
    date_from: str | None = Query(default=None, example="2025-01-01"),
    date_to: str | None = Query(default=None, example="2025-12-31"),
    sort: str = Query(default="-posted_date", description="ex: -posted_date, title, company"),
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_session),
):
    limit = max(1, min(page_size, 100))
    offset = max(0, (page - 1) * limit)


    items, total = await search_jobs(
        session=session,
        q=q,
        company=company,
        contract_type=contract_type,
        active=active,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    total_pages = max(1, math.ceil(total / limit))
    return { 
        "items": items,
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
    

@router.get("/jobs/{jobId}", response_model=JobOut)
async def get_job(
    jobId: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(JobLeaddev).where(JobLeaddev.id == jobId)
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

# Dépendance temporaire pour l'utilisateur courant (MVP)
def get_current_user_id():
    return  UUID("00000000-0000-0000-0000-000000000001")  # "demo" user_id, à remplacer par auth plus tard

# Router pour les jobs sauvegardés
# router_saved = APIRouter(prefix="/api", tags=["saved_jobs"])

@router.post("/saved-jobs", response_model=SavedJobOut)
async def create_saved_job(
    data: SavedJobCreate,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    saved = await save_job(session, user_id, data.job_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Job not found")
    # Récupérer le job pour l'output
    job = await session.get(JobLeaddev, saved.job_id)
    job_lite = None
    if job:
        from app.schemas.saved_job import JobOutLite
        job_lite = JobOutLite.model_validate(job)
    return SavedJobOut(
        id=saved.id,
        job_id=saved.job_id,
        status=getattr(saved, 'status', None),
        note=getattr(saved, 'note', None),
        applied_at=getattr(saved, 'applied_at', None),
        follow_up_at=getattr(saved, 'follow_up_at', None),
        created_at=getattr(saved, 'created_at', None),
        job=job_lite
    )

@router.get("/saved-jobs")
async def get_saved_jobs(
    status: str = None,
    q: str = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    return await list_saved_jobs(session, user_id, status, q, page, page_size)

@router.get("/saved-jobs/ids", response_model=list[UUID])
async def get_saved_job_ids_endpoint(
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    return await get_saved_job_ids(session, user_id)

@router.patch("/saved-jobs/{saved_id}", response_model=SavedJobOut)
async def patch_saved_job(
    saved_id: int,
    payload: SavedJobUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    saved = await update_saved_job(session, user_id, saved_id, payload)
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    job = await session.get(JobLeaddev, saved.job_id)
    job_lite = None
    if job:
        from app.schemas.saved_job import JobOutLite
        job_lite = JobOutLite.model_validate(job)
    return SavedJobOut(
        id=saved.id,
        job_id=saved.job_id,
        status=getattr(saved, 'status', None),
        note=getattr(saved, 'note', None),
        applied_at=getattr(saved, 'applied_at', None),
        follow_up_at=getattr(saved, 'follow_up_at', None),
        created_at=getattr(saved, 'created_at', None),
        job=job_lite
    )

@router.delete("/saved-jobs/{saved_id}")
async def delete_saved_job_endpoint(
    saved_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
):
    ok = await delete_saved_job(session, user_id, saved_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Saved job not found or not owned by user")
    return {"ok": True}