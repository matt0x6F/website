from datetime import datetime
from typing import List

import structlog
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnlyModify
from blog.models import Post
from blog.schema import PostDetails, PostMutate

logger = structlog.get_logger(__name__)

posts_router = Router()


@posts_router.get("/", response={200: List[PostDetails]}, tags=["posts"])
@paginate
def list_posts(request: HttpRequest, all: bool = False, drafts: bool = False):
    if all and request.user.is_staff:
        logger.debug(
            "Returning all posts", user=request.user.username, is_staff=request.user.is_staff
        )

        try:
            return Post.objects.all().order_by("-id")
        except Exception as err:
            logger.error("Error fetching all posts", error=err)

            raise HttpError(500, "Fail to fetch all posts") from err

    if drafts and request.user.is_staff:
        logger.debug(
            "Returning draft posts", user=request.user.username, is_staff=request.user.is_staff
        )

        try:
            return Post.objects.filter(published__isnull=True).order_by("-id")
        except Exception as err:
            logger.error("Error fetching draft posts", error=err)

            raise HttpError(500, "Fail to fetch draft posts") from err

    logger.debug(
        "Returning published posts", user=request.user.username, is_staff=request.user.is_staff
    )

    try:
        return Post.objects.filter(published__lte=datetime.now()).order_by("-published")
    except Exception as err:
        logger.error("Error fetching published posts", error=err)

        raise HttpError(500, "Fail to fetch published posts") from err


@posts_router.get("/slug/{slug}", response={200: PostDetails}, tags=["posts"])
def get_post_by_slug(request: HttpRequest, slug: str, year: int = None, draft=False):
    if request.user.is_staff:
        if draft:
            return Post.objects.filter(published__isnull=True).get(slug=slug)

        return Post.objects.filter(published__year=year).get(slug=slug)

    return (
        Post.objects.filter(published__lte=datetime.now())
        .filter(published__year=year)
        .get(slug=slug)
    )


@posts_router.get("/{id}", response={200: PostDetails}, tags=["posts"])
def get_post_by_id(request: HttpRequest, id: int):
    if request.user.is_staff:
        return Post.objects.get(id=id)
    return Post.objects.filter(published__lte=datetime.now()).get(id=id)


@posts_router.post(
    "/",
    response={201: PostDetails},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnlyModify),
)
def create_post(request: HttpRequest, post: PostMutate):
    return Post.objects.create(**post.dict(), author=request.user)


@posts_router.put(
    "/{id}",
    response={200: PostDetails},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnlyModify),
)
def update_post(request, id: int, post: PostMutate):
    # only update fields that are present in the request
    original = Post.objects.get(id=id)

    for attr, value in post.__dict__.items():
        setattr(original, attr, value)
    original.save()
    return original


@posts_router.delete(
    "/{id}", response={204: None}, tags=["posts"], auth=JWTAuth(permissions=StaffOnlyModify)
)
def delete_post(request, id: int):
    post = Post.objects.get(id=id)
    post.delete()
    return None
