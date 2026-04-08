import os
from typing import AsyncGenerator
from fastapi.datastructures import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
from app.core.config import settings
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
import os

# DATABASE_URL = os.getenv("DATABASE_URL")
# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL environment variable is not set")

url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ.get("DB_USER", "postgres.cawpdbwfbsizrtbnttgk"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST", "aws-0-eu-west-3.pooler.supabase.com"),
    port=int(os.environ.get("DB_PORT", 6543)),
    database=os.environ.get("DB_NAME", "postgres"),
    query={"sslmode": "require"}
)

engine = create_async_engine(url)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session