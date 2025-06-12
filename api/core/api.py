from enum import StrEnum

from django.contrib import admin
from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.urls import path
from ninja import Schema
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken

# Direct router imports
from accounts.api import accounts_router
from accounts.contenttypes import contenttypes_router
from accounts.groups import groups_router, permissions_router
from blog.api.comments import comments_router
from blog.api.feed import feed_router
from blog.api.files import files_router
from blog.api.posts import posts_router
from blog.api.series import series_router
from resume.api import router as resume_router

api = NinjaExtraAPI(
    title="ooo-yay.com API",
    version="1.0.0",
    description="Resource-based API for ooo-yay.com.",
    csrf=False,
)
api.register_controllers(NinjaJWTDefaultController)


# --- Custom login view that sets cookies ---
@api.post("/auth/login", operation_id="login", tags=["auth"])
def login(request, username: str, password: str):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = JsonResponse({"success": True})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
        )
        return response
    return JsonResponse({"success": False, "error": "Invalid credentials"}, status=401)


# --- Custom logout view that clears cookies ---
@api.post("/auth/logout", operation_id="logout", tags=["auth"])
def logout(request):
    response = JsonResponse({"success": True})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    django_logout(request)
    return response


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


# Register routers directly (no global auth, let routers/endpoints specify JWTAuth)
api.add_router("/accounts/", accounts_router)
api.add_router("/groups/", groups_router)
api.add_router("/permissions/", permissions_router)
api.add_router("/contenttypes/", contenttypes_router)
api.add_router("/series/", series_router)
api.add_router("/posts/", posts_router)
api.add_router("/files/", files_router)
api.add_router("/comments/", comments_router)
api.add_router("/feed/", feed_router)
api.add_router("/resume/", resume_router)

urlpatterns = [
    path("api/", api.urls),
    path("django-admin/", admin.site.urls),
]
