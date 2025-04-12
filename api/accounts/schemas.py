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


class AdminUserDetails(Schema):
    """
    Specifies fields that admins can see
    """

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    date_joined: datetime
    last_login: Optional[datetime] = None
    avatar_link: Optional[str] = None
    groups: List[Group]
    user_permissions: List[Permission]
    notes: Optional[str] = None


class AdminUserModify(Schema):
    """
    Specifies fields that admins can change
    """

    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_staff: Optional[bool] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    avatar_link: Optional[str] = None
    groups: Optional[List[Group]] = None
    user_permissions: Optional[List[Permission]] = None
    notes: Optional[str] = None


class UserSelf(Schema):
    """
    Specifies fields that users can see about themselves
    """

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
    """
    Specifies fields that users can provide to create an account
    """

    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class UpdateAccount(Schema):
    """
    Specifies fields that users can provide to update their account
    """

    username: Optional[str] = None
    email: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_link: Optional[str] = None
