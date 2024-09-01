from functools import lru_cache
from pathlib import Path
from typing import List

import structlog
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

logger = structlog.get_logger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent


class Database(BaseModel):
    name: str
    user: str
    password: str
    host: str
    port: int


class CORS(BaseModel):
    allowed_origins: List[str] = ["*"]


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(CURRENT_DIR / ".env", CURRENT_DIR / ".env.prod"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    debug: bool = False
    database: Database
    allowed_hosts: List[str] = ["*"]
    cors: CORS
    secret_key: str


@lru_cache()
def get_config() -> Configuration:
    return Configuration()
