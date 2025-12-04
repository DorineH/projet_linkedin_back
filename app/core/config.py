from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List
import os

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_ENV: str = "dev"
    CORS_ORIGINS: List[AnyHttpUrl] | List[str] = ["http://localhost:5173"]

       # Pydantic v2 : transforme "a,b" -> ["a","b"]
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


class Config:
    env_file = ".env"
    case_sensitive = True


settings = Settings()