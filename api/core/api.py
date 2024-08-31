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

from auth.middleware import JWTAuth, StaffOnlyModify

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


@api.get("/health")
def add(request) -> HealthResponse:
    """
    Returns a simple health check response.
    """
    return {"status": "ok"}


api.add_router("/accounts/", "accounts.api.router")
api.add_router("/posts/", "blog.api.posts_router", auth=JWTAuth(permissions=StaffOnlyModify))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
