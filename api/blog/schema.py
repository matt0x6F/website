from datetime import datetime
from typing import List, Optional

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


class PostSummary(Schema):
    id: int
    title: str
    published: Optional[datetime] = None
    slug: str


class ValidationErrorResponse(Schema):
    detail: str


class FileDetails(Schema):
    id: int
    name: str
    content_type: str
    charset: Optional[str]
    size: int
    location: str
    created_at: datetime
    posts: List[PostSummary]
    visibility: str


class FileMetadata(Schema):
    posts: Optional[List[int]] = None
    visibility: str = "public"


class FileMutateMetadata(Schema):
    posts: Optional[List[int]] = None
