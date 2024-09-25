from datetime import datetime
from typing import Optional

from ninja import Schema


class UserSelf(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_active: bool
    date_joined: datetime
    avatar_link: Optional[str] = None


class AuthError(Schema):
    details: str


class NewAccount(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
