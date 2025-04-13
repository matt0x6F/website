import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import structlog
from pydantic import BaseModel, ValidationError
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

logger = structlog.get_logger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent


class S3(BaseModel):
    model_config = {"extra": "allow"}

    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    bucket_name: str = ""
    endpoint_url: str = ""
    prefix: str = ""
    cdn_endpoint: str = ""


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
        # right side is preferred
        env_file=(CURRENT_DIR / ".env", CURRENT_DIR / os.getenv("ENV_FILE", ".env.prod")),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    debug: bool = False
    database: Database
    allowed_hosts: List[str] = ["*"]
    cors: CORS
    secret_key: str
    s3: Optional[S3] = S3()


@lru_cache()
def get_config() -> Configuration:
    try:
        config = Configuration()
    except ValidationError as e:
        logger.exception(f"Error loading configuration: {e}")
        raise e
    return config


config = get_config()
