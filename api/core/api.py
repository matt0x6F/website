from enum import StrEnum

from django.contrib import admin
from django.urls import path
from ninja import Schema
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

# Direct router imports
from accounts.api import accounts_router
from accounts.contenttypes import contenttypes_router
from accounts.groups import groups_router, permissions_router
from auth.middleware import JWTAuth, StaffOnly, StaffOnlyModify
from blog.api.comments import comments_router
from blog.api.feed import feed_router
from blog.api.files import files_router
from blog.api.posts import posts_router
from blog.api.series import series_router

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


# Register routers directly
api.add_router("/accounts/", accounts_router)
api.add_router("/groups/", groups_router, auth=JWTAuth(permissions=StaffOnly))
api.add_router("/permissions/", permissions_router, auth=JWTAuth(permissions=StaffOnly))
api.add_router("/contenttypes/", contenttypes_router)
api.add_router("/series/", series_router, auth=JWTAuth())
api.add_router("/posts/", posts_router, auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/files/", files_router, auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/comments/", comments_router, auth=JWTAuth())
api.add_router("/feed/", feed_router, auth=JWTAuth())

urlpatterns = [
    path("api/", api.urls),
    path("django-admin/", admin.site.urls),
]
