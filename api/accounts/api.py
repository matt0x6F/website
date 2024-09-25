import structlog
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError, ValidationError

from accounts.models import User
from accounts.schemas import AuthError, NewAccount, UserSelf
from auth.middleware import JWTAuth

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)  # noqa: F821
router = Router()


@router.get("/whoami", auth=JWTAuth(), response={200: UserSelf, 401: AuthError}, tags=["accounts"])
def whoami(request: HttpRequest):
    """
    Returns the calling users details
    """

    logger.debug("User self-identification", user=request.user)

    if request.user == AnonymousUser():
        raise HttpError(401, "Token invalid")

    return request.user


@router.get("/sign_up", auth=JWTAuth(), response={200: UserSelf, 403: AuthError}, tags=["accounts"])
def sign_up(request: HttpRequest, new_acct_details: NewAccount):
    """
    Creates a new user
    """
    if request.user != AnonymousUser():
        raise HttpError(403, "This operation is not allowed")

    try:
        user = User.objects.create(**new_acct_details.dict())
    except Exception as e:
        raise ValidationError([e]) from e

    return user
