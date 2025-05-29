from typing import List, Optional

from django.http import HttpRequest
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate

from auth.middleware import JWTAuth, StaffOnly
from blog.schema.comment import (
    AdminCommentList,
    AdminCommentUpdate,
    CommentCreate,
    CommentList,
    CommentMutate,
)

from ..models import Comment, Post

comments_router = Router()


@comments_router.get(
    "/",
    response={200: List[CommentList]},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
    operation_id="listComments",
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
    operation_id="modQueueList",
)
@paginate
def mod_queue_list(request: HttpRequest, reviewed: Optional[bool] = False):
    try:
        comments = Comment.objects.filter(reviewed=reviewed)
    except Exception as err:
        raise HttpError(500, "Fail to fetch all comments") from err

    return comments


@comments_router.put(
    "/moderation/{id}",
    response={200: AdminCommentList},
    tags=["moderation"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    operation_id="modUpdateComment",
)
def mod_update_comment(request: HttpRequest, id: int, comment: AdminCommentUpdate):
    try:
        original = Comment.objects.get(id=id)

        for attr, value in comment.__dict__.items():
            setattr(original, attr, value)
        # If staff did this there's no reason to add it to the review queue
        original.reviewed = True
        original.save()
    except Exception as err:
        raise ValidationError("Comment with this id already exists") from err
    return original


@comments_router.get(
    "/moderation/{id}",
    response={200: AdminCommentList},
    tags=["moderation"],
    auth=JWTAuth(permissions=StaffOnly, allow_anonymous=False),
    operation_id="modGetComment",
)
def mod_get_comment(request: HttpRequest, id: int):
    """
    Gets all the details of a comment for moderation.
    """
    try:
        return Comment.objects.get(id=id)
    except Exception as err:
        raise HttpError(500, "Fail to fetch comment") from err


@comments_router.get(
    "/{id}",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=True),
    operation_id="getComment",
)
def get_comment(request: HttpRequest, id: int):
    """
    Gets all the details of a comment.
    """
    try:
        return Comment.objects.get(id=id)
    except Exception as err:
        raise HttpError(500, "Fail to fetch comment") from err


@comments_router.post(
    "/",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
    operation_id="createComment",
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
        raise HttpError(500, "Fail to fetch post") from err

    try:
        created = Comment.objects.create(
            content=comment.content, post=post, author=request.user, parent=parent
        )
    except Exception as err:
        raise ValidationError("Comment with this id already exists") from err

    return created


@comments_router.put(
    "/{id}",
    response={200: CommentList},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
    operation_id="updateComment",
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
    except Exception as err:
        raise ValidationError("Comment with this id already exists") from err


@comments_router.delete(
    "/{id}",
    response={200: None},
    tags=["comments"],
    auth=JWTAuth(permissions=None, allow_anonymous=False),
    operation_id="deleteComment",
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
            raise HttpError(500, "Fail to delete comment") from err
