from typing import Optional

from ninja import Schema
from pydantic import Field


class UserPublic(Schema):
    id: int
    username: str
    email: Optional[str] = None
    is_staff: bool = False


class AuthorSummary(Schema):
    id: int
    username: str
    name: Optional[str] = Field(None, description="The author's name")
    url: Optional[str] = Field(
        None,
        description="The URL of a site owned by the author. It could be a blog, micro-blog, Twitter account, etc.",
    )
    avatar: Optional[str] = Field(
        None,
        description="The URL for an image for the author. Should be square and relatively large — such as 512 x 512 pixels.",
    )
