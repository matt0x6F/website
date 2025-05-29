from typing import List, Optional

import structlog
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly
from blog.schema.file import FileDetails
from blog.schema.post import (
    PostCreate,
    PostListPublic,
    PostPublic,
    PostUpdate,
)
from blog.schema.sharecode import ShareCodeCreate, ShareCodeSchema
from blog.schema.validation import ValidationErrorResponse

from ..models import Post, Series, ShareCode

logger = structlog.get_logger(__name__)

posts_router = Router()


# POST API ENDPOINTS (These are the ones we are keeping and have updated)
@posts_router.post(
    "",
    response={201: PostPublic, 400: ValidationErrorResponse},
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    tags=["posts"],
    operation_id="createPost",
)
def create_post(request, payload: PostCreate):
    """
    Create a new blog post.
    If slug is not provided, it will be generated from the title.
    `series_id` can be provided to associate the post with a series.
    """
    data = payload.dict()
    if not data.get("slug") and data.get("title"):
        data["slug"] = slugify(data["title"])

    if (
        data.get("slug")
        and Post.objects.filter(
            slug=data["slug"], published_at__isnull=False if not data.get("published_at") else True
        ).exists()
    ):
        return 400, {
            "detail": f"Post with slug '{data['slug']}' already exists for the publication status."
        }

    if payload.series_id:
        get_object_or_404(Series, id=payload.series_id)

    post = Post.objects.create(author=request.user, **data)
    return 201, post


@posts_router.put(
    "/{post_id}",
    response={200: PostPublic, 400: ValidationErrorResponse, 404: None},
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    tags=["posts"],
    operation_id="updatePost",
)
def update_post(request, post_id: int, payload: PostUpdate):
    """
    Update an existing blog post. All fields in payload are optional.
    `series_id` can be provided or set to `null` to disassociate from a series.
    """
    post = get_object_or_404(Post, id=post_id, author=request.user)
    data = payload.dict(exclude_unset=True)

    if "title" in data and ("slug" not in data or not data["slug"]):
        data["slug"] = slugify(data["title"])

    if (
        data.get("slug")
        and data["slug"] != post.slug
        and Post.objects.filter(
            slug=data["slug"],
            published_at__isnull=False if not data.get("published_at", post.published_at) else True,
        )
        .exclude(id=post_id)
        .exists()
    ):
        return 400, {
            "detail": f"Post with slug '{data['slug']}' already exists for the publication status."
        }

    if "series_id" in data:
        if data["series_id"] is not None:
            get_object_or_404(Series, id=data["series_id"])

    for attr, value in data.items():
        setattr(post, attr, value)
    post.save()
    post.refresh_from_db()
    return 200, post


@posts_router.get(
    "/{post_id}",
    response=PostPublic,
    tags=["posts"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
    operation_id="getPostById",
)
def get_post_by_id(request, post_id: int):
    if request.user.is_authenticated and request.user.is_staff:
        post = get_object_or_404(Post.objects.select_related("author", "series"), id=post_id)
    else:
        post = get_object_or_404(
            Post.objects.select_related("author", "series"),
            id=post_id,
            published_at__isnull=False,
        )
    return post


@posts_router.get(
    "/slug/{year}/{slug}",
    response=PostPublic,
    tags=["posts"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
    operation_id="getPostBySlugAndYear",
)
def get_post_by_slug_and_year(
    request, year: int, slug: str, draft: bool = False, sharecode: str = None
):
    # 1. Always try to fetch the published post first (ignore sharecode if found)
    try:
        post = Post.objects.select_related("author", "series").get(
            slug=slug, published_at__year=year, published_at__isnull=False
        )
        return post
    except Post.DoesNotExist:
        pass
    # 2. If not found, and sharecode is present, try to fetch the unpublished post and validate sharecode
    if sharecode:
        try:
            post = Post.objects.select_related("author", "series").get(
                slug=slug, published_at__isnull=True
            )
            valid_code = ShareCode.objects.filter(post=post, code=sharecode).first()
            if not valid_code:
                raise Post.DoesNotExist()
            if valid_code.expires_at and valid_code.expires_at < timezone.now():
                raise Post.DoesNotExist()
            return post
        except Post.DoesNotExist as err:
            raise HttpError(404, "Post not found") from err
    # 3. If not found, check staff/draft logic (for staff direct draft access)
    try:
        if request.user.is_authenticated and request.user.is_staff:
            if draft:
                post = get_object_or_404(Post, slug=slug, published_at__isnull=True)
            else:
                post = get_object_or_404(Post, slug=slug, published_at__year=year)
        else:
            raise Post.DoesNotExist()
    except Post.DoesNotExist as err:
        raise HttpError(404, "Post not found") from err
    return post


@posts_router.get(
    "",
    response=List[PostListPublic],
    tags=["posts"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
    operation_id="listPosts",
)
@paginate
def list_posts(
    request,
    series_slug: Optional[str] = None,
    author_id: Optional[int] = None,
    drafts: bool = False,
    all_posts: bool = False,  # Combines drafts and published
    order: str = None,  # Will set default below
):
    """
    List posts, optionally filtered by series, author, or draft status.
    The 'order' parameter controls the ordering of posts. Use '-published_at' (default for published), '-updated_at' (default for drafts).
    """
    posts = Post.objects.select_related("author", "series").all()
    is_staff = request.user.is_authenticated and request.user.is_staff

    if not is_staff:
        posts = posts.filter(published_at__isnull=False)
        if drafts or all_posts:
            return Post.objects.none()
    else:
        if all_posts:
            pass
        elif drafts:
            posts = posts.filter(published_at__isnull=True)
        else:
            posts = posts.filter(published_at__isnull=False)

    if series_slug:
        posts = posts.filter(series__slug=series_slug)
    if author_id:
        posts = posts.filter(author_id=author_id)

    # Determine allowed orders and default order
    if drafts:
        allowed_orders = ["-updated_at", "updated_at"]
        if not order:
            order = "-updated_at"
    else:
        allowed_orders = ["-published_at", "published_at"]
        if not order:
            order = "-published_at"

    if order not in allowed_orders:
        raise HttpError(400, f"Invalid order parameter. Allowed: {allowed_orders}")

    posts = posts.order_by(order)

    return posts


@posts_router.get(
    "/{post_id}/files",
    response={200: List[FileDetails]},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=True),
    operation_id="getPostFilesById",
)
def get_post_files_by_id(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return post.files.all()


@posts_router.delete(
    "/{post_id}",
    response={204: None},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    operation_id="deletePost",
)
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return None


@posts_router.get(
    "/{post_id}/sharecodes",
    response=List[ShareCodeSchema],
    auth=JWTAuth(permissions=StaffOnly),
    tags=["posts"],
    operation_id="listSharecodes",
)
def list_sharecodes(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return post.sharecodes.all()


@posts_router.post(
    "/{post_id}/sharecodes",
    response=ShareCodeSchema,
    auth=JWTAuth(permissions=StaffOnly),
    tags=["posts"],
    operation_id="createSharecode",
)
def create_sharecode(request, post_id: int, payload: ShareCodeCreate):
    from django.utils.crypto import get_random_string

    post = get_object_or_404(Post, id=post_id)
    code = get_random_string(16)
    sharecode = ShareCode.objects.create(
        code=code,
        post=post,
        note=payload.note,
        expires_at=payload.expires_at,
    )
    return sharecode


@posts_router.delete(
    "/{post_id}/sharecodes/{code}",
    response={204: None},
    auth=JWTAuth(permissions=StaffOnly),
    tags=["posts"],
    operation_id="deleteSharecode",
)
def delete_sharecode(request, post_id: int, code: str):
    post = get_object_or_404(Post, id=post_id)
    sharecode = get_object_or_404(ShareCode, post=post, code=code)
    sharecode.delete()
    return 204
