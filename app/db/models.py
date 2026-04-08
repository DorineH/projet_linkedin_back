from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, DateTime, Integer, UniqueConstraint
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class JobLeaddev(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jobId: Mapped[str | None] = mapped_column(String(255), unique=True)
    title: Mapped[str | None] = mapped_column(String(500))
    company: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column("location", String(255))
    url: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    contract_type: Mapped[str | None] = mapped_column(String(100))
    posted_date: Mapped[object | None] = mapped_column(DateTime(timezone=False))
    scraped_at: Mapped[object | None] = mapped_column(DateTime(timezone=False))
    updated_at: Mapped[object | None] = mapped_column(DateTime(timezone=False))
    active: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str | None] = mapped_column(Text)


class UserSavedJob(Base):
    __tablename__ = "user_saved_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uix_user_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(Text, default="saved")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    updated_at: Mapped[object | None] = mapped_column(DateTime(timezone=False), nullable=True)