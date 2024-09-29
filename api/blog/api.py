from typing import List, Literal

import structlog
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.utils import timezone
from ninja import File as NinjaFile
from ninja import Router, UploadedFile
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly, StaffOnlyModify
from blog.models import File, Post
from blog.schema import (
    FileDetails,
    FileMetadata,
    FileMutateMetadata,
    PostDetails,
    PostMutate,
    ValidationErrorResponse,
)
from files.storage import PrivateStorage, PublicStorage

logger = structlog.get_logger(__name__)

posts_router = Router()
files_router = Router()


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


@posts_router.get("/slug/{slug}", response={200: PostDetails}, tags=["posts"])
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


@posts_router.get("/{id}", response={200: PostDetails}, tags=["posts"])
def get_post_by_id(request: HttpRequest, id: int):
    if request.user.is_staff:
        return Post.objects.get(id=id)
    return Post.objects.filter(published__lte=timezone.now()).get(id=id)


@posts_router.get("/{id}/files", response={200: List[FileDetails]}, tags=["posts"])
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
