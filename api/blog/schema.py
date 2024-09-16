from datetime import datetime
from typing import Optional

from ninja import Schema


class PostMutate(Schema):
    title: str
    content: str
    published: Optional[datetime] = None
    slug: str


class PostDetails(Schema):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    published: Optional[datetime] = None
    author_id: int
    slug: str


class ValidationErrorResponse(Schema):
    detail: str
