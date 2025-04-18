"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from enum import StrEnum

from django.contrib import admin
from django.urls import path
from ninja import Schema
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from auth.middleware import JWTAuth, StaffOnly, StaffOnlyModify
from blog.schemas import JSONFeed

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


@api.get("feed.json", summary="JSON Feed", response=JSONFeed)
def feed(request) -> JSONFeed:
    """
    Returns a JSON Feed compliant with version 1.1 of the specification.
    See: https://www.jsonfeed.org/version/1.1/
    """
    return JSONFeed(
        title="Blog Feed",
        home_page_url="https://example.org/",
        feed_url="https://example.org/feed.json",
        description="Latest blog posts",
        items=[],  # TODO: Implement fetching actual blog posts
    )


api.add_router("/accounts/", "accounts.api.accounts_router")
api.add_router("/groups/", "accounts.groups.groups_router", auth=JWTAuth(permissions=StaffOnly))
api.add_router(
    "/permissions/", "accounts.groups.permissions_router", auth=JWTAuth(permissions=StaffOnly)
)
api.add_router("/contenttypes/", "accounts.contenttypes.contenttypes_router")
api.add_router("/posts/", "blog.api.posts_router", auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/files/", "blog.api.files_router", auth=JWTAuth(permissions=StaffOnlyModify))
api.add_router("/comments/", "blog.api.comments_router", auth=JWTAuth())


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", api.urls),
]
