from typing import List, Literal

import structlog
from django.http import HttpRequest
from ninja import File as NinjaFile
from ninja import Router, UploadedFile
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly
from blog.schema.file import FileDetails, FileMetadata, FileMutateMetadata, OrphanedFiles
from files.storage import PrivateStorage, PublicStorage

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
    operation_id="updateFile",
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
    "/{id}",
    response={200: None},
    tags=["files"],
    auth=JWTAuth(permissions=StaffOnly),
    operation_id="deleteFile",
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
