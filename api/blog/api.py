from typing import List, Literal, Optional

import structlog
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.utils import timezone
from ninja import File as NinjaFile
from ninja import Router, UploadedFile
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate
from ninja.responses import Response

from auth.middleware import JWTAuth, StaffOnly, StaffOnlyModify
from blog.feed_builder import FeedBuilder
from blog.models import Comment, File, Post
from blog.schema import (
    AdminCommentList,
    AdminCommentUpdate,
    CommentCreate,
    CommentList,
    CommentMutate,
    FileDetails,
    FileMetadata,
    FileMutateMetadata,
    PostDetails,
    PostMutate,
    ValidationErrorResponse,
)
from blog.schemas import Author, FeedItem, JSONFeed
from files.storage import PrivateStorage, PublicStorage

logger = structlog.get_logger(__name__)

posts_router = Router()
files_router = Router()
comments_router = Router()
feed_router = Router()


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
        .with_authors([Author(name="Matt Ouille", url="https://ooo-yay.com")])
        .with_description("Latest posts from @ooo-yay")
        .with_icon("https://ooo-yay.com/logo.svg")
        .with_favicon("https://ooo-yay.com/logo.svg")
        .with_feed_url("https://ooo-yay.com/api/feed/")
        .with_home_page_url("https://ooo-yay.com")
    )

    posts = Post.objects.filter(published__lte=timezone.now()).order_by("-published")[
        offset : offset + limit
    ]
    for post in posts:
        builder.add_item(
            FeedItem(
                id=f"{post.id}",
                title=post.title,
                content_html=post.content,
                date_published=post.published,
                date_modified=post.updated_at,
                language="en",
                author=Author(name="Matt Ouille", url="https://ooo-yay.com"),
                url=f"https://ooo-yay.com/posts/{post.published.year}/{post.slug}",
            )
        )

    count = Post.objects.filter(published__lte=timezone.now()).count()
    if offset + limit < count:
        builder.with_next_url(f"https://ooo-yay.com/feed.json?limit={limit}&offset={offset+limit}")

    return Response(builder.build(), content_type="application/feed+json")


#
# Posts
#


@posts_router.get("/", auth=JWTAuth(None, True), response={200: List[PostDetails]}, tags=["posts"])
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
            today = timezone.now()
            # published is null OR published is in the future
            return Post.objects.filter(
                Q(published__isnull=True) | Q(published__gte=today)
            ).order_by("-id")
        except Exception as err:
            logger.error("Error fetching draft posts", error=err)

            raise HttpError(500, "Fail to fetch draft posts") from err

    logger.debug(
        "Returning published posts",
        user=request.user.username,
        is_staff=request.user.is_staff,
        method=request.method,
    )

    try:
        return Post.objects.filter(published__lte=timezone.now()).order_by("-published")
    except Exception as err:
        logger.error("Error fetching published posts", error=err)

        raise HttpError(500, "Fail to fetch published posts") from err


@posts_router.get(
    "/slug/{slug}", auth=JWTAuth(None, True), response={200: PostDetails}, tags=["posts"]
)
def get_post_by_slug(request: HttpRequest, slug: str, year: int = None, draft=False):
    if request.user.is_staff:
        if draft:
            return Post.objects.filter(published__isnull=True).get(slug=slug)

        return Post.objects.filter(published__year=year).get(slug=slug)

    return (
        Post.objects.filter(published__lte=timezone.now())
        .filter(published__year=year)
        .get(slug=slug)
    )


@posts_router.get("/{id}", auth=JWTAuth(None, True), response={200: PostDetails}, tags=["posts"])
def get_post_by_id(request: HttpRequest, id: int):
    if request.user.is_staff:
        return Post.objects.get(id=id)
    return Post.objects.filter(published__lte=timezone.now()).get(id=id)


@posts_router.get(
    "/{id}/files", auth=JWTAuth(StaffOnly, True), response={200: List[FileDetails]}, tags=["posts"]
)
def get_post_files_by_id(request: HttpRequest, id: int):
    post = Post.objects.get(id=id)
    return post.files.all()


@posts_router.post(
    "/",
    response={200: PostDetails, 422: ValidationErrorResponse},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnlyModify),
)
def create_post(request: HttpRequest, post: PostMutate):
    try:
        post = Post.objects.create(**post.dict(), author=request.user)
    except IntegrityError as err:
        logger.error("Error creating post", error=err)

        raise ValidationError("Post with this slug already exists") from err
    return post


@posts_router.put(
    "/{id}",
    response={200: PostDetails, 422: ValidationErrorResponse},
    tags=["posts"],
    auth=JWTAuth(permissions=StaffOnlyModify),
)
def update_post(request, id: int, post: PostMutate):
    try:
        # only update fields that are present in the request
        original = Post.objects.get(id=id)

        for attr, value in post.__dict__.items():
            setattr(original, attr, value)
        original.save()
    except IntegrityError as err:
        logger.error("Error creating post", error=err)

        raise ValidationError("Post with this slug already exists") from err
    return original


@posts_router.delete(
    "/{id}", response={204: None}, tags=["posts"], auth=JWTAuth(permissions=StaffOnlyModify)
)
def delete_post(request, id: int):
    post = Post.objects.get(id=id)
    post.delete()
    return None


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
