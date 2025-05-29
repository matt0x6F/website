from datetime import datetime
from typing import List, Optional

from ninja import Schema

from .post import PostSummary


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


class OrphanedFileDetails(Schema):
    name: str
    size: int
    content_type: str
    location: str
    last_modified: Optional[datetime]
    visibility: str


class OrphanedFiles(Schema):
    public: List[OrphanedFileDetails]
    private: List[OrphanedFileDetails]
