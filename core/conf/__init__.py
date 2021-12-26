from typing import Optional
from pydantic import BaseSettings


class EnvironmentSettings(BaseSettings):
    DATABASE_URI: Optional[str] = "sqlite://db.sqlite3"
    ADMIN_TOKEN: str
    # API_KEY: str
    # API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = EnvironmentSettings()

__all__ = ['settings', ]
