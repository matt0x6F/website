from django.http import HttpRequest
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from accounts.schemas import UserSelf

router = Router()


@router.get("/whoami", auth=JWTAuth(), response=UserSelf, tags=["accounts"])
def whoami(request: HttpRequest):
    """
    Returns the calling users details
    """
    return request.user
