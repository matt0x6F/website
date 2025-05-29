from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import Field


class SeriesBase(Schema):
    title: str = Field(..., max_length=200)
    slug: str = Field(
        ...,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-friendly identifier. Will be auto-generated from title if not provided.",
    )
    description: Optional[str] = None


class SeriesCreate(SeriesBase):
    pass


class SeriesUpdate(Schema):
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = None


class SeriesPublic(SeriesBase):
    id: int
    created_at: datetime
    updated_at: datetime
    post_count: int = 0


class PostSummaryForSeries(Schema):
    id: int
    title: str
    slug: str
    year: Optional[int] = None
    published_at: Optional[datetime] = None


class SeriesDetailPublic(SeriesPublic):
    posts: List[PostSummaryForSeries] = []


class SeriesListResponse(Schema):
    items: List[SeriesPublic]
    count: int


class SeriesSummary(Schema):
    id: int
    title: str
