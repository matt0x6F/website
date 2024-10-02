from datetime import datetime
from typing import List, Optional

from ninja import Schema


class ContentType(Schema):
    id: int
    app_label: str
    model: str
    name: str
    app_labeled_name: str


class Permission(Schema):
    id: int
    name: str
    codename: str
    content_type: ContentType


class Group(Schema):
    id: int
    name: str
    permissions: List[Permission]


class UserDetails(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    date_joined: datetime
    last_login: datetime
    avatar_link: Optional[str] = None
    groups: List[Group]
    user_permissions: List[Permission]


class UserModify(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    date_joined: datetime
    last_login: datetime
    avatar_link: Optional[str] = None
    groups: List[Group]
    user_permissions: List[Permission]


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


class UpdateAccount(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
