from datetime import datetime
from typing import List, Optional

from ninja import Schema

from .post import PostDetails
from .user import AuthorSummary


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
