from typing import List

import structlog
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate

from accounts.schemas import AuthError, GroupMutate, PermissionMutate
from accounts.schemas import Group as GroupSchema
from accounts.schemas import Permission as PermissionSchema
from auth.middleware import JWTAuth, StaffOnly

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
groups_router = Router(auth=JWTAuth(permissions=StaffOnly))
permissions_router = Router(auth=JWTAuth(permissions=StaffOnly))


# Groups API endpoints
@groups_router.get(
    "/",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: List[GroupSchema], 403: AuthError},
    tags=["groups"],
)
@paginate
def list_groups(request: HttpRequest):
    """
    Returns a list of all groups
    """
    try:
        groups = Group.objects.all()
    except Exception as e:
        raise ValidationError([e]) from e

    return groups


@groups_router.post(
    "/",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: GroupSchema, 403: AuthError},
    tags=["groups"],
)
def create_group(request: HttpRequest, group_data: GroupMutate):
    """
    Creates a new group
    """
    try:
        group = Group.objects.create(name=group_data.name)
        if group_data.permissions:
            group.permissions.set(group_data.permissions)
        group.save()
    except Exception as e:
        raise ValidationError([e]) from e

    return group


@groups_router.put(
    "/{group_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: GroupSchema, 403: AuthError},
    tags=["groups"],
)
def update_group(request: HttpRequest, group_id: int, group_data: GroupMutate):
    """
    Updates a group
    """
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist as err:
        raise HttpError(404, "Group not found") from err

    try:
        group.name = group_data.name
        if group_data.permissions is not None:
            group.permissions.set(group_data.permissions)
        group.save()
    except Exception as e:
        raise ValidationError([e]) from e

    return group


@groups_router.delete(
    "/{group_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: None, 403: AuthError},
    tags=["groups"],
)
def delete_group(request: HttpRequest, group_id: int):
    """
    Deletes a group
    """
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist as err:
        raise HttpError(404, "Group not found") from err

    try:
        group.delete()
    except Exception as e:
        raise ValidationError([e]) from e

    return None


# Permissions API endpoints
@permissions_router.get(
    "/",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: List[PermissionSchema], 403: AuthError},
    tags=["permissions"],
)
@paginate
def list_permissions(request: HttpRequest):
    """
    Returns a list of all permissions
    """
    try:
        permissions = Permission.objects.all()
    except Exception as e:
        raise ValidationError([e]) from e

    return permissions


@permissions_router.post(
    "/",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: PermissionSchema, 403: AuthError},
    tags=["permissions"],
)
def create_permission(request: HttpRequest, permission_data: PermissionMutate):
    """
    Creates a new permission
    """
    try:
        content_type = ContentType.objects.get(id=permission_data.content_type.id)
        permission = Permission.objects.create(
            name=permission_data.name,
            codename=permission_data.codename,
            content_type=content_type,
        )
    except Exception as e:
        raise ValidationError([e]) from e

    return permission


@permissions_router.put(
    "/{permission_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: PermissionSchema, 403: AuthError},
    tags=["permissions"],
)
def update_permission(request: HttpRequest, permission_id: int, permission_data: PermissionMutate):
    """
    Updates a permission
    """
    try:
        permission = Permission.objects.get(pk=permission_id)
    except Permission.DoesNotExist as err:
        raise HttpError(404, "Permission not found") from err

    try:
        content_type = ContentType.objects.get(id=permission_data.content_type.id)
        permission.name = permission_data.name
        permission.codename = permission_data.codename
        permission.content_type = content_type
        permission.save()
    except Exception as e:
        raise ValidationError([e]) from e

    return permission
