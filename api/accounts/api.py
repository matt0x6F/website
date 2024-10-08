from typing import List

import structlog
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate
from ninja_jwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from accounts.models import User
from accounts.schemas import AuthError, NewAccount, UpdateAccount, UserDetails, UserModify, UserSelf
from auth.middleware import JWTAuth, StaffOnly

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)  # noqa: F821
accounts_router = Router()


@accounts_router.get(
    "/me", auth=JWTAuth(), response={200: UserSelf, 403: AuthError}, tags=["accounts"]
)
def whoami(request: HttpRequest):
    """
    Returns the calling users details
    """

    logger.debug("User self-identification", user=request.user)

    if request.user == AnonymousUser():
        raise HttpError(403, "Token invalid")

    return request.user


@accounts_router.put(
    "/me",
    auth=JWTAuth(),
    response={200: UserSelf, 403: AuthError},
    tags=["accounts"],
)
def update_self(request: HttpRequest, new_details: UpdateAccount):
    """
    Updates the calling users details
    """

    if request.user == AnonymousUser():
        raise HttpError(403, "Token invalid")

    # pop these out so we can handle them separately
    old_password = new_details.dict().pop("old_password", None)
    new_password = new_details.dict().pop("new_password", None)

    for key, value in new_details.dict().items():
        setattr(request.user, key, value)

    # password changes are a specific workflow
    if old_password and new_password:
        if not request.user.check_password(old_password):
            raise HttpError(403, "Password incorrect")

        # encrypt the password
        request.user.set_password(new_password)

    request.user.save()

    return request.user


@accounts_router.delete(
    "/me",
    auth=JWTAuth(),
    response={200: None, 403: AuthError},
    tags=["accounts"],
)
def delete_self(request: HttpRequest):
    """
    Deletes the calling user
    """

    if request.user == AnonymousUser():
        raise HttpError(403, "Token invalid")

    try:
        # blacklist all refresh tokens for this user
        outstanding_tokens = OutstandingToken.objects.filter(user=request.user)

        for token in outstanding_tokens:
            BlacklistedToken.objects.create(token=token)
    except IntegrityError:
        logger.debug("Token already blacklisted", token=token.__str__)
    except Exception as e:
        raise ValidationError([e]) from e

    try:
        request.user.delete()
    except Exception as e:
        logger.error("Failed to delete user", user=request.user, error=e)

        raise ValidationError([e]) from e

    return


@accounts_router.post(
    "/sign_up", auth=JWTAuth(), response={200: UserSelf, 403: AuthError}, tags=["accounts"]
)
def sign_up(request: HttpRequest, new_acct_details: NewAccount):
    """
    Creates a new user
    """

    new_acct_details_dict = new_acct_details.dict()

    password = new_acct_details_dict.pop("password")

    if request.user != AnonymousUser():
        raise HttpError(403, "This operation is not allowed")

    try:
        user = User.objects.create(**new_acct_details_dict, is_active=True)
        user.set_password(password)
        user.save()

    except Exception as e:
        raise ValidationError([e]) from e

    return user


@accounts_router.get(
    "/",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: List[UserDetails], 403: AuthError},
    tags=["accounts"],
)
@paginate
def list_users(request: HttpRequest):
    """
    Returns a list of all users
    """
    try:
        users = User.objects.all()
    except Exception as e:
        raise ValidationError([e]) from e

    return users


@accounts_router.get(
    "/{user_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: UserDetails, 403: AuthError},
    tags=["accounts"],
)
def get_user(request: HttpRequest, user_id: int):
    """
    Returns a specific user
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as err:
        raise HttpError(404, "User not found") from err

    return user


@accounts_router.put(
    "/{user_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: UserDetails, 403: AuthError},
    tags=["accounts"],
)
def update_user(request: HttpRequest, user_id: int, new_details: UserModify):
    """
    Updates a user
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as err:
        raise HttpError(404, "User not found") from err

    for key, value in new_details.dict().items():
        if key != "password":
            setattr(user, key, value)
        else:
            # encrypt the password
            user.set_password(value)

    user.save()

    return user


@accounts_router.delete(
    "/{user_id}",
    auth=JWTAuth(permissions=StaffOnly),
    response={200: None, 403: AuthError},
    tags=["accounts"],
)
def delete_user(request: HttpRequest, user_id: int):
    """
    Deletes a user
    """
    try:
        user = User.objects.get(pk=user_id)

        # blacklist all refresh tokens for this user
        outstanding_tokens = OutstandingToken.objects.filter(user=user)

        for token in outstanding_tokens:
            BlacklistedToken.objects.create(token=token)
    except User.DoesNotExist as err:
        raise HttpError(404, "User not found") from err

    try:
        user.delete()
    except Exception as e:
        logger.error("Failed to delete user", user=user, error=e)

        raise ValidationError([e]) from e

    return None
