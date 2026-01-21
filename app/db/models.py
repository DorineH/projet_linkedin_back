# app/db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, DateTime, Integer

class Base(DeclarativeBase):
    pass

class JobLeaddev(Base):
    __tablename__ = "jobs"
# jobs pour la bdd supabase connecté à n8n
# jobs_leaddev pour la bdd supabase connecté à dbeaver
    # PK en base = serial4 => Integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # UNIQUE en base
    jobId: Mapped[str | None] = mapped_column(String(255), unique=True)

    # Colonnes texte (on peut rester en Text, mais tu peux aussi respecter les tailles si tu veux)
    title: Mapped[str | None] = mapped_column(String(500))
    company: Mapped[str | None] = mapped_column(String(255))

    # Le nom de colonne en base est "location" (avec guillemets dans le DDL),
    # on l'indique explicitement pour éviter tout doute.
    location: Mapped[str | None] = mapped_column("location", String(255))

    url: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    contract_type: Mapped[str | None] = mapped_column(String(100))

    # En base : timestamp sans timezone -> timezone=False
    posted_date: Mapped[object | None] = mapped_column(DateTime(timezone=False))
    scraped_at: Mapped[object | None] = mapped_column(DateTime(timezone=False))
    updated_at: Mapped[object | None] = mapped_column(DateTime(timezone=False))

    active: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str | None] = mapped_column(Text)
