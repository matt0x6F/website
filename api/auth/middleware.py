from typing import Any, Type

import structlog
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_jwt.authentication import InvalidToken, JWTAuth

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

TOKEN_UNSET = "undefined"


class StaffOnlyModify:
    "Simple permission that allows modify only to superuser"

    def check(request: HttpRequest, user: AbstractUser):
        if request.method == "GET":
            return
        if not request.user.is_staff:
            logger.info(
                "User attempted to access restricted endpoint and was rejected",
                user=user,
                permission="StaffOnlyModify",
                method=request.method,
                path=request.path,
            )

            raise HttpError(403, "This operation is not allowed")


class AuthenticatedOnly:
    "Simple permission that allows modify only to authenticated users"

    def check(request: HttpRequest, user: AbstractUser):
        if request.user.is_anonymous:
            raise HttpError(403, "This operation is not allowed")


class AnonymousOnly:
    "Simple permission that allows modify only to superuser"

    def check(request: HttpRequest, user: AbstractUser):
        if not request.user.is_anonymous:
            raise HttpError(403, "This operation is not allowed")


class StaffOnly:
    "Simple permission that allows modify only to superuser"

    def check(request: HttpRequest, user: AbstractUser):
        # if user is anonymous, reject them
        if request.user.is_anonymous:
            logger.info(
                "User attempted to access restricted endpoint and was rejected",
                user=user,
                permission="StaffOnly",
            )

            raise HttpError(403, "This operation is not allowed")

        if not user.is_staff:
            logger.info(
                "User attempted to access restricted endpoint and was rejected",
                user=user,
                permission="StaffOnly",
                method=request.method,
                path=request.path,
            )

            raise HttpError(403, "This operation is not allowed")


class JWTAuth(JWTAuth):
    def __init__(self, permissions=None, allow_anonymous=False):
        super().__init__()
        self.permissions = permissions
        self.allow_anonymous = allow_anonymous

    def __call__(self, request: HttpRequest) -> Any | None:
        headers = request.headers
        auth_value = headers.get(self.header)
        if auth_value is not None:
            parts = auth_value.split(" ")

            if parts[0].lower() != self.openapi_scheme:
                if settings.DEBUG:
                    logger.error(f"Unexpected auth - '{auth_value}'")
                return None
            token = " ".join(parts[1:])
        else:
            token = TOKEN_UNSET

        user: AbstractUser = AnonymousUser()

        try:
            user = self.authenticate(request, token)
            request.user = user
        except Exception:
            logger.error("Failed to authenticate user")

        if not self.permissions:
            return user

        return self.authorize(request, user)

    def authenticate(self, request: HttpRequest, token: str) -> Type[AbstractUser]:
        user: AbstractUser = AnonymousUser()

        if token == TOKEN_UNSET:
            logger.debug("Token is not set; defaulting to AnonymousUser")

            return user

        try:
            logger.debug("Authenticating user with token", token=token)

            user = super().jwt_authenticate(request, token)

            logger.info("Successfully authenticated user", user=user)
        except InvalidToken:
            logger.error("Token is invalid; defaulting to AnonymousUser")

        except Exception:
            logger.error("Failed to authenticate user; defaulting to AnonymousUser")

        return user

    def authorize(self, request: HttpRequest, user: AbstractUser) -> Type[AbstractUser]:
        if self.permissions:
            logger.info(
                "Authorizing request",
                user=str(user),
                method=request.method,
                path=request.path,
                permissions=str(self.permissions),
            )
            try:
                self.permissions.check(request, user)
                logger.info(
                    "Authorization granted",
                    user=str(user),
                    method=request.method,
                    path=request.path,
                    permissions=str(self.permissions),
                )
            except Exception as e:
                logger.error(
                    "Authorization denied",
                    user=str(user),
                    method=request.method,
                    path=request.path,
                    permissions=str(self.permissions),
                    error=str(e),
                )
                raise
        return user
