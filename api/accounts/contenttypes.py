from django.contrib.contenttypes.models import ContentType
from ninja_extra import Router

from accounts.schemas import ContentType as ContentTypeSchema
from auth.middleware import JWTAuth, StaffOnly

contenttypes_router = Router(auth=JWTAuth(permissions=StaffOnly))


@contenttypes_router.get("/", response=list[ContentTypeSchema], summary="List content types")
def list_content_types(request) -> list[ContentTypeSchema]:
    """
    List all available content types in the system.
    Content types represent the models available in the Django application.
    This endpoint is restricted to staff users only as it's primarily used for administrative purposes.
    """
    content_types = ContentType.objects.all().order_by("app_label", "model")
    return [
        {
            "id": ct.id,
            "app_label": ct.app_label,
            "model": ct.model,
            "name": ct.name,
            "app_labeled_name": f"{ct.app_label}.{ct.model}",
        }
        for ct in content_types
    ]
