from datetime import datetime
from typing import List

import structlog
from django.http import HttpRequest
from ninja import Router
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

        return Post.objects.all().order_by("-id")

    if drafts and request.user.is_staff:
        logger.debug(
            "Returning draft posts", user=request.user.username, is_staff=request.user.is_staff
        )

        return Post.objects.filter(published__is_null=True).order_by("-id")

    logger.debug(
        "Returning published posts", user=request.user.username, is_staff=request.user.is_staff
    )

    print(f"USER: {request.user.username} {request.user.is_staff}")

    return Post.objects.filter(published__lte=datetime.now()).order_by("-published")


@posts_router.get("/slug/{slug}", response={200: PostDetails}, tags=["posts"])
def get_post_by_slug(request, slug: str):
    return Post.objects.get(slug=slug)


@posts_router.get("/{id}", response={200: PostDetails}, tags=["posts"])
def get_post_by_id(request, id: int):
    return Post.objects.get(id=id)


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
