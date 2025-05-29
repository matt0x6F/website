from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import Field

from .series import SeriesPublic, SeriesSummary
from .user import UserPublic  # Assuming user schema is in user.py


class PostBase(Schema):
    title: str = Field(..., max_length=200)
    content: str
    published_at: Optional[datetime] = None
    series_id: Optional[int] = Field(None, description="ID of the series this post belongs to")


class PostCreate(PostBase):
    slug: Optional[str] = Field(
        None,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-friendly identifier. Will be auto-generated from title if not provided and not present.",
    )


class PostUpdate(Schema):
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    series_id: Optional[int] = Field(None, description="ID of the series this post belongs to")


class PostPublic(PostBase):
    id: int
    slug: str
    author: UserPublic
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0
    series: Optional[SeriesPublic] = Field(
        None, description="Full details of the series this post belongs to"
    )


class PostListPublic(PostPublic):
    pass


class PostListResponse(Schema):
    items: List[PostListPublic]
    count: int
    offset: Optional[int] = None
    limit: Optional[int] = None


class PostDetails(Schema):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    published: Optional[datetime] = None
    author_id: int
    slug: str
    series: Optional["SeriesSummary"] = None


class PostSummary(Schema):
    id: int
    title: str
    published: Optional[datetime] = None
    slug: str
