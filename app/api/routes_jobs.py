import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import JobLeaddev
from app.db.session import get_session
from app.schemas.job import JobOut, JobsResponse
from app.services.job_service import search_jobs


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
