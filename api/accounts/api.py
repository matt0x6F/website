from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError, ValidationError

from accounts.models import User
from accounts.schemas import NewAccount, UserSelf
from auth.middleware import JWTAuth

router = Router()


@router.get("/whoami", auth=JWTAuth(), response=UserSelf, tags=["accounts"])
def whoami(request: HttpRequest):
    """
    Returns the calling users details
    """
    return request.user


@router.get("/sign_up", auth=JWTAuth(), response=UserSelf, tags=["accounts"])
def sign_up(request: HttpRequest, new_acct_details: NewAccount):
    """
    Creates a new user
    """
    if request.user != AnonymousUser():
        raise HttpError(401, "This operation is not allowed")

    try:
        user = User.objects.create(**new_acct_details.dict())
    except Exception as e:
        raise ValidationError([e]) from e

    return user
