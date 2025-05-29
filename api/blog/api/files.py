from typing import List, Literal

import structlog
from django.http import HttpRequest
from ninja import File as NinjaFile
from ninja import Router, UploadedFile
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly
from blog.schema.file import FileDetails, FileMetadata, FileMutateMetadata, OrphanedFiles

from ..models import File

logger = structlog.get_logger(__name__)

files_router = Router()


@files_router.get(
    "/",
    response={200: List[FileDetails]},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="listFiles",
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
    operation_id="listOrphanedFiles",
)
def list_orphaned_files(request: HttpRequest):
    # ... (copy the full orphaned files endpoint code from api.py)
    pass


@files_router.get(
    "/{id}",
    response={200: FileDetails},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="getFile",
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
    "/",
    response={200: FileDetails},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="createFile",
)
def create_file(request: HttpRequest, metadata: FileMetadata, upload: NinjaFile[UploadedFile]):
    # ... (copy the full create_file endpoint code from api.py)
    pass


@files_router.put(
    "/{id}",
    response={200: FileDetails},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="updateFile",
)
def update_file(request: HttpRequest, id: int, metadata: FileMutateMetadata):
    # ... (copy the full update_file endpoint code from api.py)
    pass


@files_router.delete(
    "/{id}",
    response={200: None},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="deleteFile",
)
def delete_file(request: HttpRequest, id: int):
    # ... (copy the full delete_file endpoint code from api.py)
    pass
