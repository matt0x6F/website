from typing import Any, Type

import structlog
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

logger = structlog.get_logger(__name__)


class StaffOnlyModify:
    "Simple permission that allows modify only to superuser"

    def check(request: HttpRequest, user: AbstractUser):
        if request.method == "GET":
            return
        if not user.is_staff:
            logger.info(
                "User attempted to access restricted endpoint and was rejected",
                user=user,
                permission="StaffOnlyModify",
                method=request.method,
                path=request.path,
            )

            raise HttpError(401, "This operation is not allowed")


class StaffOnly:
    "Simple permission that allows modify only to superuser"

    def check(request: HttpRequest, user: AbstractUser):
        if not user.is_staff:
            logger.info(
                "User attempted to access restricted endpoint and was rejected",
                user=user,
                permission="StaffOnly",
                method=request.method,
                path=request.path,
            )

            raise HttpError(401, "This operation is not allowed")


class JWTAuth(JWTAuth):
    def __init__(self, permissions=None, allow_anonymous=False):
        super().__init__()
        self.permissions = permissions
        self.allow_anonymous = allow_anonymous

    def __call__(self, request: HttpRequest) -> Any | None:
        headers = request.headers
        auth_value = headers.get(self.header)
        if not auth_value:
            return AnonymousUser()  # if there is no key, we return AnonymousUser object
        parts = auth_value.split(" ")

        if parts[0].lower() != self.openapi_scheme:
            if settings.DEBUG:
                logger.error(f"Unexpected auth - '{auth_value}'")
            return None
        token = " ".join(parts[1:])

        try:
            user = self.authenticate(request, token)
            request.user = user
            return user
        except Exception as e:
            logger.error("Failed to authenticate user", exception=e)

            return AnonymousUser()

        return

    def authenticate(self, request: HttpRequest, token: str) -> Type[AbstractUser]:
        user: AbstractUser = AnonymousUser()
        try:
            logger.debug("Authenticating user with token", token=token)

            user = super().jwt_authenticate(request, token)

            logger.info("Successfully authenticated user", user=user)

        except Exception as e:
            logger.debug("Failed to authenticate user; defaulting to AnonymousUser", exception=e)

        if self.permissions:
            logger.debug("Checking permissions for user", user=user)

            self.permissions.check(request, user)

            logger.debug("User has required permissions", user=user)

        return user
