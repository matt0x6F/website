from typing import List, Optional, Union

from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly
from blog.schema.series import (
    PostSummaryForSeries,
    SeriesCreate,
    SeriesDetailPublic,
    SeriesPublic,
    SeriesUpdate,
)
from blog.schema.validation import ValidationErrorResponse

from ..models import Series

series_router = Router()


@series_router.delete(
    "/{series_id}",
    response={204: None},
    auth=JWTAuth(permissions=StaffOnly),
    tags=["series"],
    operation_id="deleteSeries",
)
def delete_series(request, series_id: int):
    """
    Delete a series. Posts belonging to this series will have their 'series' field set to NULL.
    Prevent deletion if any posts are still associated with the series.
    """
    series = get_object_or_404(Series, id=series_id)
    if series.posts.exists():
        raise HttpError(400, "You must disassociate all posts from this series before deleting it.")
    series.delete()
    return 204


# SERIES API ENDPOINTS
@series_router.post(
    "",
    response=SeriesPublic,
    auth=JWTAuth(permissions=StaffOnly),
    tags=["series"],
    operation_id="createSeries",
)
def create_series(request, payload: SeriesCreate):
    """
    Create a new series. Title and slug are required.
    Slug is auto-generated from title if not provided or if an empty string is passed.
    """
    if not payload.slug or payload.slug.strip() == "":
        payload.slug = slugify(payload.title)

    # Check for slug uniqueness before creating
    if Series.objects.filter(slug=payload.slug).exists():
        return ValidationErrorResponse(
            detail=f"Series with slug '{payload.slug}' already exists."
        )  # This should be a 400/422

    series = Series.objects.create(**payload.dict())
    return series


@series_router.get(
    "",
    response=List[SeriesPublic],
    tags=["series"],
    operation_id="listSeries",
)
@paginate
def list_series(request, include_posts_count: bool = False):
    """
    List all series. Use `include_posts_count=true` to get the number of posts in each series.
    """
    series_qs = Series.objects.all()
    if include_posts_count:
        # Only count published posts
        series_qs = series_qs.annotate(
            post_count=Count("posts", filter=models.Q(posts__published_at__isnull=False))
        )
    return series_qs


@series_router.get(
    "/{series_id}",
    response=SeriesDetailPublic,
    tags=["series"],
    operation_id="getSeriesDetailById",
)
def get_series_detail_by_id(
    request, series_id: int, include_posts: bool = True, posts_limit: int = 10
):
    """
    Retrieve a single series by its ID.
    Includes a list of associated posts (summaries) by default.
    Use `include_posts=false` to omit posts.
    Use `posts_limit` to control the number of posts returned.
    """
    series = get_object_or_404(Series, id=series_id)

    series_data = SeriesPublic.from_orm(series).dict()
    series_data["post_count"] = series.posts.filter(
        published_at__isnull=False
    ).count()  # Only published

    if include_posts:
        post_qs = series.posts.filter(published_at__isnull=False).order_by("-published_at")[
            :posts_limit
        ]
        posts_summary = []
        for post in post_qs:
            summary = PostSummaryForSeries.from_orm(post).dict()
            if post.published_at:
                summary["year"] = post.published_at.year
            posts_summary.append(summary)
        series_data["posts"] = posts_summary
    else:
        series_data["posts"] = []

    return series_data  # Return as dict because SeriesDetailPublic expects 'posts'


@series_router.get(
    "/slug/{slug}",
    response=SeriesDetailPublic,
    tags=["series"],
    operation_id="getSeriesDetailBySlug",
)
def get_series_detail_by_slug(
    request, slug: str, include_posts: bool = True, posts_limit: int = 10
):
    """
    Retrieve a single series by its slug.
    Includes a list of associated posts (summaries) by default.
    Use `include_posts=false` to omit posts.
    Use `posts_limit` to control the number of posts returned.
    """
    series = get_object_or_404(Series, slug=slug)

    series_data = SeriesPublic.from_orm(series).dict()
    series_data["post_count"] = series.posts.filter(
        published_at__isnull=False
    ).count()  # Only published

    if include_posts:
        post_qs = series.posts.filter(published_at__isnull=False).order_by("-published_at")[
            :posts_limit
        ]
        posts_summary = []
        for post in post_qs:
            summary = PostSummaryForSeries.from_orm(post).dict()
            if post.published_at:
                summary["year"] = post.published_at.year
            posts_summary.append(summary)
        series_data["posts"] = posts_summary
    else:
        series_data["posts"] = []

    return series_data  # Return as dict because SeriesDetailPublic expects 'posts'


@series_router.put(
    "/{series_id}",
    response=SeriesPublic,
    auth=JWTAuth(permissions=StaffOnly),
    tags=["series"],
    operation_id="updateSeries",
)
def update_series(request, series_id: int, payload: SeriesUpdate):
    """
    Update an existing series. All fields in payload are optional.
    If slug is provided and changed, it will be updated.
    If title is changed and slug is not provided (or empty), slug might be regenerated.
    """
    series = get_object_or_404(Series, id=series_id)
    payload_data = payload.dict(exclude_unset=True)

    if "title" in payload_data and ("slug" not in payload_data or not payload_data["slug"]):
        new_slug = slugify(payload_data["title"])
        if (
            new_slug != series.slug
            and Series.objects.filter(slug=new_slug).exclude(id=series_id).exists()
        ):
            # This should be a 400/422 error
            return ValidationErrorResponse(
                detail=f"Another series with slug '{new_slug}' already exists."
            )
        series.slug = (
            new_slug  # Update slug if title changed and slug wasn't manually set to something else
        )

    for attr, value in payload_data.items():
        setattr(series, attr, value)

    series.save()
    # Re-fetch to get potentially updated slug and other model-generated fields correctly
    series.refresh_from_db()
    annotated_series = Series.objects.annotate(post_count=Count("posts")).get(id=series_id)
    return annotated_series


@series_router.get(
    "/{series_id_or_slug}/posts",
    response=List[PostSummaryForSeries],
    tags=["series"],
    operation_id="listPostsInSeries",
)
@paginate
def list_posts_in_series(
    request,
    series_id_or_slug: Union[int, str],
    exclude_post_id: Optional[int] = None,
    order: str = "-published_at",  # New parameter
):
    """
    List all published posts belonging to a specific series.
    Optionally exclude a specific post by its ID (e.g., the current post being viewed).
    The 'order' parameter controls the ordering of posts. Use '-published_at' (default) for descending, 'published_at' for ascending.
    """
    if isinstance(series_id_or_slug, int):
        series = get_object_or_404(Series, id=series_id_or_slug)
    else:
        series = get_object_or_404(Series, slug=series_id_or_slug)

    # Validate order param
    allowed_orders = ["-published_at", "published_at"]
    if order not in allowed_orders:
        raise HttpError(400, f"Invalid order parameter. Allowed: {allowed_orders}")

    posts_qs = series.posts.filter(published_at__isnull=False).order_by(order)
    if exclude_post_id:
        posts_qs = posts_qs.exclude(id=exclude_post_id)

    # The @paginate decorator will handle creating PostSummaryForSeries from the queryset items
    # if the response schema is List[PostSummaryForSeries] and PostSummaryForSeries.from_orm exists
    return posts_qs
