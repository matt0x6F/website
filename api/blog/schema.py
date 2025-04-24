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


class AuthorSummary(Schema):
    id: int
    username: str


class CommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    children: List["CommentList"]
    created_at: datetime
    updated_at: datetime
    post: PostDetails


class AdminChildCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    children: Optional[List["AdminCommentList"]] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminParentCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    parent: Optional["AdminParentCommentList"] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    children: Optional[List["AdminChildCommentList"]] = None
    parent: Optional["AdminParentCommentList"] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminCommentUpdate(Schema):
    visible: Optional[bool] = None
    note: Optional[str] = None
    reviewed: bool


class CommentMutate(Schema):
    content: str


class CommentCreate(Schema):
    content: str
    parent_id: Optional[int] = None
    post_id: int


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
