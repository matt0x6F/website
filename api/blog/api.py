from typing import List, Literal, Optional, Union

import structlog
from django.db import models

# from config.utils.permissions import StaffPermission # Commented out problematic import
from django.db.models import Count
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from ninja import File as NinjaFile
from ninja import Router, UploadedFile
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate
from ninja.responses import Response
from pydantic import BaseModel

from auth.middleware import JWTAuth, StaffOnly
from blog.feed_builder import FeedBuilder
from blog.models import Comment, File, Post, Series
from blog.schema import (
    AdminCommentList,
    AdminCommentUpdate,
    CommentCreate,
    CommentList,
    CommentMutate,
    FeedAuthorSchema,
    FeedItem,
    FileDetails,
    FileMetadata,
    FileMutateMetadata,
    JSONFeed,
    OrphanedFiles,
    PostCreate,
    PostListPublic,
    PostPublic,
    PostSummaryForSeries,
    PostUpdate,
    SeriesCreate,
    SeriesDetailPublic,
    SeriesPublic,
    SeriesUpdate,
    ValidationErrorResponse,
)
from files.storage import PrivateStorage, PublicStorage

logger = structlog.get_logger(__name__)

posts_router = Router()
files_router = Router()
comments_router = Router()
feed_router = Router()
series_router = Router()


class FeedAuthor(BaseModel):
    name: str
    url: str


#
# Feed
#


@feed_router.get(
    "/",
    auth=JWTAuth(None, True),
    response={200: JSONFeed},
    tags=["feed"],
)
def feed(request: HttpRequest, limit: int = 10, offset: int = 0):
    builder = (
        FeedBuilder(title="ooo-yay feed")
        .with_authors([FeedAuthorSchema(name="Matt Ouille", url="https://ooo-yay.com")])
        .with_description("Latest posts from @ooo-yay")
        .with_icon("https://ooo-yay.com/logo.svg")
        .with_favicon("https://ooo-yay.com/logo.svg")
        .with_feed_url("https://ooo-yay.com/api/feed/")
        .with_home_page_url("https://ooo-yay.com")
    )

    posts = Post.objects.filter(published_at__lte=timezone.now()).order_by("-published_at")[
        offset : offset + limit
    ]
    for post in posts:
        builder.add_item(
            FeedItem(
                id=f"{post.id}",
                title=post.title,
                content_html=post.content,
                date_published=post.published_at,
                date_modified=post.updated_at,
                language="en",
                author=FeedAuthorSchema(name="Matt Ouille", url="https://ooo-yay.com"),
                url=f"https://ooo-yay.com/posts/{post.published_at.year}/{post.slug}",
            )
        )

    count = Post.objects.filter(published_at__lte=timezone.now()).count()
    if offset + limit < count:
        builder.with_next_url(
            f"https://ooo-yay.com/feed.json?limit={limit}&offset={offset + limit}"
        )

    return Response(builder.build(), content_type="application/feed+json")


#
# Files
#


@files_router.get(
    "/", response={200: List[FileDetails]}, tags=["files"], auth=JWTAuth(permissions=StaffOnly)
)
@paginate
def list_files(request: HttpRequest, visibility: Literal["public", "private", "all"] = "all"):
    """
    List all files
    """
    try:
        if visibility == "public":
            return File.objects.filter(visibility="public")
        elif visibility == "private":
            return File.objects.filter(visibility="private")
        else:
            return File.objects.all()
    except Exception as err:
        logger.error("Error fetching all files", error=err)

        raise HttpError(500, "Fail to fetch all files") from err


@files_router.get(
    "/orphaned",
    response={200: OrphanedFiles},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
)
def list_orphaned_files(request: HttpRequest):
    """
    Find files that exist in storage but not in the database.
    If a file exists in both public and private storage, it will be considered public.
    Returns detailed metadata about each orphaned file.
    """
    try:
        # Get all files from database
        db_files = set(File.objects.values_list("name", flat=True))
        logger.info("Files in database", files=list(db_files))

        # Initialize storage backends
        public_storage = PublicStorage()
        private_storage = PrivateStorage()

        # List files from public storage
        public_files = set()
        orphaned_public_details = []
        try:
            # Debug: Print storage configuration
            logger.info(
                "Public storage config",
                bucket=public_storage.bucket_name,
                location=public_storage.location,
            )

            # Get all objects and log them
            prefix = public_storage.location.rstrip("/") + "/" if public_storage.location else ""
            all_objects = list(public_storage.bucket.objects.filter(Prefix=prefix))
            logger.info("Raw public bucket objects", objects=[obj.key for obj in all_objects])

            # Create a mapping of full keys to objects for easier lookup
            public_object_map = {obj.key: obj for obj in all_objects if obj.key != prefix}

            # Remove the prefix from the keys to match database names
            public_files = {
                key[len(prefix) :] if prefix else key for key in public_object_map.keys()
            }

            logger.info("Files in public storage (without prefix)", files=list(public_files))
            logger.info("Orphaned public files", files=list(public_files - db_files))

            # Get details for each orphaned public file
            for filename in public_files - db_files:
                try:
                    file_obj = public_storage.open(filename)
                    # Get the object using the full key from our mapping
                    full_key = prefix + filename if prefix else filename
                    obj = public_object_map.get(full_key)

                    if obj:
                        logger.info(
                            "Found orphaned public file",
                            filename=filename,
                            full_key=full_key,
                            size=obj.size,
                        )
                        orphaned_public_details.append(
                            {
                                "name": filename,
                                "size": obj.size,
                                "content_type": getattr(
                                    file_obj, "content_type", "application/octet-stream"
                                ),
                                "location": public_storage.url(filename),
                                "last_modified": obj.last_modified,
                                "visibility": "public",
                            }
                        )
                    else:
                        logger.error(
                            "Failed to get object details", filename=filename, full_key=full_key
                        )
                except Exception as err:
                    logger.error("Error getting public file details", error=err, filename=filename)
        except Exception as err:
            logger.error("Error listing public files", error=err)

        # List files from private storage
        private_files = set()
        orphaned_private_details = []
        try:
            # Get all objects and log them
            prefix = private_storage.location.rstrip("/") + "/" if private_storage.location else ""
            all_objects = list(private_storage.bucket.objects.filter(Prefix=prefix))
            logger.info("Raw private bucket objects", objects=[obj.key for obj in all_objects])

            # Create a mapping of full keys to objects for easier lookup
            private_object_map = {obj.key: obj for obj in all_objects if obj.key != prefix}

            # Remove the prefix from the keys to match database names
            private_files = {
                key[len(prefix) :] if prefix else key for key in private_object_map.keys()
            }

            # Remove any files that exist in public storage
            private_files = private_files - public_files

            logger.info("Files in private storage (without prefix)", files=list(private_files))
            logger.info("Orphaned private files", files=list(private_files - db_files))

            # Get details for each orphaned private file
            for filename in private_files - db_files:
                try:
                    file_obj = private_storage.open(filename)
                    # Get the object using the full key from our mapping
                    full_key = prefix + filename if prefix else filename
                    obj = private_object_map.get(full_key)

                    if obj:
                        logger.info(
                            "Found orphaned private file",
                            filename=filename,
                            full_key=full_key,
                            size=obj.size,
                        )
                        orphaned_private_details.append(
                            {
                                "name": filename,
                                "size": obj.size,
                                "content_type": getattr(
                                    file_obj, "content_type", "application/octet-stream"
                                ),
                                "location": private_storage.url(filename),
                                "last_modified": obj.last_modified,
                                "visibility": "private",
                            }
                        )
                    else:
                        logger.error(
                            "Failed to get object details", filename=filename, full_key=full_key
                        )
                except Exception as err:
                    logger.error("Error getting private file details", error=err, filename=filename)
        except Exception as err:
            logger.error("Error listing private files", error=err)

        return {"public": orphaned_public_details, "private": orphaned_private_details}

    except Exception as err:
        logger.error("Error listing orphaned files", error=err)
        raise HttpError(500, "Failed to list orphaned files") from err


@files_router.get(
    "/{id}", response={200: FileDetails}, tags=["files"], auth=JWTAuth(permissions=StaffOnly)
)
def get_file(request: HttpRequest, id: int):
    """
    Gets all the details of a file.
    """
    try:
        return File.objects.get(id=id)
    except Exception as err:
        logger.error("Error fetching file", error=err)

        raise HttpError(500, "Fail to fetch file") from err


@files_router.post(
    "/", response={200: FileDetails}, tags=["files"], auth=JWTAuth(permissions=StaffOnly)
)
def create_file(request: HttpRequest, metadata: FileMetadata, upload: NinjaFile[UploadedFile]):
    """
    Creates a file with or without post associations.
    """
    try:
        if metadata.visibility == "public":
            stored_name = PublicStorage().save(upload.name, upload.file)

            url = PublicStorage().url(stored_name)
        else:
            stored_name = PrivateStorage().save(upload.name, upload.file)

            url = PrivateStorage().url(stored_name)

        upload = File.objects.create(
            location=url,
            name=stored_name,
            content_type=upload.content_type,
            charset=upload.charset,
            size=upload.size,
            visibility=metadata.visibility,
        )

        if metadata:
            upload.posts.set(metadata.posts)

        return upload
    except Exception as err:
        import sys

        print("Error creating file:", err, file=sys.stderr)
        logger.error("Error creating file", error=err)

        raise HttpError(500, "Fail to create file") from err


@files_router.put(
    "/{id}",
    response={200: FileDetails},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
)
def update_file(request: HttpRequest, id: int, metadata: FileMutateMetadata):
    """
    Updates a file, namely the posts associated with the file. File properties are immutable.
    """
    try:
        file = File.objects.get(id=id)

        if metadata.posts:
            file.posts.set(metadata.posts)

        # TODO: changing visibility here requires recreating the object and updating the DB
    except Exception as err:
        logger.error("Error associating file", error=err)

        raise HttpError(500, "Fail to associate file") from err

    return file


@files_router.delete(
    "/{id}", response={200: None}, tags=["files"], auth=JWTAuth(permissions=StaffOnly)
)
def delete_file(request: HttpRequest, id: int):
    """
    Deletes a file from the database and S3.
    """
    try:
        file = File.objects.get(id=id)
        file.delete()

    except Exception as err:
        logger.error("Error deleting file", error=err)

        raise HttpError(500, "Fail to delete file") from err

    logger.info(
        "Deleting file from S3",
        file=file.name,
        id=file.id,
        location=file.location,
        name=file.name,
        visiblity=file.visibility,
    )

    try:
        if file.visibility == "public":
            PublicStorage().delete(file.name)
        else:
            PrivateStorage().delete(file.name)
    except Exception as err:
        logger.error("Error deleting file from S3", error=err)

        raise err

    return None


#
# Comments
#


@comments_router.get(
    "/",
    response={200: List[CommentList]},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
)
@paginate
def list_comments(
    request: HttpRequest,
    post_id: int | None = None,
    top_level: bool = False,
):
    """
    List all comments for a post
    """
    if post_id is None and not request.user.is_staff:
        raise HttpError(403, "You do not have permission to view all comments")

    comments = Comment.objects.all()

    if post_id:
        try:
            comments = comments.filter(post_id=post_id)
        except Exception as err:
            logger.error("Error fetching all comments", error=err)

            raise HttpError(500, "Fail to fetch all comments") from err

    if top_level:
        comments = comments.filter(parent__isnull=True)

    # go through the children field of each comment and pop items where visible is False
    for comment in comments:
        if not comment.visible:
            comments.pop(comment)

    return comments


@comments_router.get(
    "/moderation/queue",
    response={200: List[AdminCommentList]},
    tags=["moderation"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
)
@paginate
def mod_queue_list(request: HttpRequest, reviewed: Optional[bool] = False):
    try:
        comments = Comment.objects.filter(reviewed=reviewed)
    except Exception as err:
        logger.error("Error fetching all comments", error=err)

        raise HttpError(500, "Fail to fetch all comments") from err

    return comments


@comments_router.put(
    "/moderation/{id}",
    response={200: AdminCommentList},
    tags=["moderation"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
)
def mod_update_comment(request: HttpRequest, id: int, comment: AdminCommentUpdate):
    try:
        original = Comment.objects.get(id=id)

        for attr, value in comment.__dict__.items():
            setattr(original, attr, value)
        # If staff did this there's no reason to add it to the review queue
        original.reviewed = True
        original.save()
    except IntegrityError as err:
        logger.error("Error updating comment", error=err)

        raise ValidationError("Comment with this id already exists") from err
    return original


@comments_router.get(
    "/{id}",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
)
def get_comment(request: HttpRequest, id: int):
    """
    Gets all the details of a comment.
    """
    try:
        return Comment.objects.get(id=id)
    except Exception as err:
        logger.error("Error fetching comment", error=err)

        raise HttpError(500, "Fail to fetch comment") from err


@comments_router.post(
    "/",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
)
def create_comment(request: HttpRequest, comment: CommentCreate):
    """
    Creates a comment
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        raise HttpError(401, "You must be logged in to create a comment")

    parent = None
    if comment.parent_id:
        try:
            parent = Comment.objects.get(id=comment.parent_id)
        except Exception:
            parent = None

    try:
        post = Post.objects.get(id=comment.post_id)
    except Exception as err:
        logger.error("Error fetching post", error=err)

        raise HttpError(500, "Fail to fetch post") from err

    try:
        created = Comment.objects.create(
            content=comment.content, post=post, author=request.user, parent=parent
        )
    except IntegrityError as err:
        logger.error("Error creating comment", error=err)

        raise ValidationError("Comment with this id already exists") from err

    return created


@comments_router.put(
    "/{id}",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
)
def update_comment(request, id: int, comment: CommentMutate):
    # Only allow editing comments if the user is the author, the comment is visible, and if it's been less than an hour after the comment was made
    try:
        original = Comment.objects.get(id=id)
        if (
            original.author != request.user
            or not original.visible
            or (timezone.now() - original.created_at).seconds > 3600
        ):
            raise HttpError(403, "You do not have permission to edit this comment")

        for attr, value in comment.__dict__.items():
            setattr(original, attr, value)
        # If the author did this, add it to the review queue
        original.reviewed = False
        original.save()

        return original
    except IntegrityError as err:
        logger.error("Error creating comment", error=err)

        raise ValidationError("Comment with this id already exists") from err


@comments_router.delete(
    "/{id}",
    response={200: None},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
)
def delete_comment(request: HttpRequest, id: int):
    # only delete a comment if the user is staff or if they are the author, if the comment is visible, and if it's been less than an hour since the comment was made
    if request.user.is_staff:
        comment = Comment.objects.get(id=id)
        comment.delete()
    else:
        try:
            comment = Comment.objects.get(id=id)
            if (
                comment.author != request.user
                or not comment.visible
                or (timezone.now() - comment.created_at).seconds > 3600
            ):
                raise HttpError(403, "You do not have permission to delete this comment")
            comment.delete()
        except Exception as err:
            logger.error("Error deleting comment", error=err)

            raise HttpError(500, "Fail to delete comment") from err


#
# Series
#


@series_router.delete(
    "/{series_id}", response={204: None}, auth=JWTAuth(permissions=StaffOnly), tags=["series"]
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
@series_router.post("", response=SeriesPublic, auth=JWTAuth(permissions=StaffOnly), tags=["series"])
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


@series_router.get("", response=List[SeriesPublic], tags=["series"])
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


@series_router.get("/{series_id}", response=SeriesDetailPublic, tags=["series"])
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


@series_router.get("/slug/{slug}", response=SeriesDetailPublic, tags=["series"])
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
    "/{series_id}", response=SeriesPublic, auth=JWTAuth(permissions=StaffOnly), tags=["series"]
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
    "/{series_id_or_slug}/posts", response=List[PostSummaryForSeries], tags=["series"]
)  # Could be paginated too
@paginate
def list_posts_in_series(
    request, series_id_or_slug: Union[int, str], exclude_post_id: Optional[int] = None
):
    """
    List all published posts belonging to a specific series.
    Optionally exclude a specific post by its ID (e.g., the current post being viewed).
    """
    if isinstance(series_id_or_slug, int):
        series = get_object_or_404(Series, id=series_id_or_slug)
    else:
        series = get_object_or_404(Series, slug=series_id_or_slug)

    posts_qs = series.posts.filter(published_at__isnull=False).order_by("-published_at")
    if exclude_post_id:
        posts_qs = posts_qs.exclude(id=exclude_post_id)

    # The @paginate decorator will handle creating PostSummaryForSeries from the queryset items
    # if the response schema is List[PostSummaryForSeries] and PostSummaryForSeries.from_orm exists
    return posts_qs


#
# Posts
#


# POST API ENDPOINTS (These are the ones we are keeping and have updated)
@posts_router.post(
    "",
    response={201: PostPublic, 400: ValidationErrorResponse},
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    tags=["posts"],
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
)
def get_post_by_slug_and_year(request, year: int, slug: str, draft: bool = False):
    if request.user.is_authenticated and request.user.is_staff:
        if draft:
            post = get_object_or_404(Post, slug=slug, published_at__isnull=True)
        else:
            post = get_object_or_404(Post, slug=slug, published_at__year=year)
    else:
        post = get_object_or_404(
            Post, slug=slug, published_at__year=year, published_at__isnull=False
        )
    return post


@posts_router.get(
    "",
    response=List[PostListPublic],
    tags=["posts"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
)
@paginate
def list_posts(
    request,
    series_slug: Optional[str] = None,
    author_id: Optional[int] = None,
    drafts: bool = False,
    all_posts: bool = False,  # Combines drafts and published
):
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

    return posts


@posts_router.get(
    "/{post_id}/files",
    response={200: List[FileDetails]},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=True),
)
def get_post_files_by_id(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return post.files.all()


@posts_router.delete(
    "/{post_id}",
    response={204: None},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
)
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return None
