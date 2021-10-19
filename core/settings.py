from typing import Optional

from pydantic import BaseSettings


class EnvironmentSettings(BaseSettings):
    DATABASE_URI: Optional[str] = "sqlite://db.sqlite3"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
