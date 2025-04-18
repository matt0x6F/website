from enum import StrEnum

from django.contrib import admin
from django.urls import path
from ninja import Schema
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from auth.middleware import JWTAuth, StaffOnly, StaffOnlyModify

api = NinjaExtraAPI(
    title="ooo-yay.com API",
    version="1.0.0",
    description="Resource-based API for ooo-yay.com.",
    csrf=False,
)
api.register_controllers(NinjaJWTDefaultController)


class HealthStatus(StrEnum):
    ok = "ok"
    not_ok = "not_ok"


class HealthResponse(Schema):
    status: HealthStatus


@api.get("/health", summary="Health check")
def healthcheck(request) -> HealthResponse:
    """
    Returns a simple health check response.
    """
    return {"status": "ok"}


api.add_router("/accounts/", "accounts.api.accounts_router")
api.add_router("/groups/", "accounts.groups.groups_router", auth=JWTAuth(permissions=StaffOnly))
api.add_router(
    "/permissions/", "accounts.groups.permissions_router", auth=JWTAuth(permissions=StaffOnly)
)
api.add_router("/contenttypes/", "accounts.contenttypes.contenttypes_router")
api.add_router("/posts/", "blog.api.posts_router", auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/files/", "blog.api.files_router", auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/comments/", "blog.api.comments_router", auth=JWTAuth())
api.add_router("/feed/", "blog.api.feed_router", auth=JWTAuth())

urlpatterns = [
    path("api/", api.urls),
    path("django-admin/", admin.site.urls),
]
