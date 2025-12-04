from typing import Optional

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobLeaddev


async def search_jobs(
    session: AsyncSession,
    q: Optional[str] = None,
    company: Optional[str] = None,
    contract_type: Optional[str] = None,
    active: Optional[bool] = True,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort: str = "-posted_date",
    limit: int = 20,
    offset: int = 0,
):
    """Recherche simple dans jobs_leaddev avec filtres + tri + pagination."""

    conditions = []

    # Filtre active
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

    # Requête principale
    stmt = select(JobLeaddev)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Tri
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

    # Total (pour la pagination côté front)
    if conditions:
        subq = select(JobLeaddev).where(and_(*conditions)).subquery()
        count_stmt = select(func.count()).select_from(subq)
    else:
        count_stmt = select(func.count()).select_from(JobLeaddev)

    total = (await session.execute(count_stmt)).scalar_one()

    return items, total
