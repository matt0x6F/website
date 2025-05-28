from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import Field


class UserPublic(Schema):
    id: int
    username: str
    email: Optional[str] = None
    is_staff: bool = False


class SeriesSummary(Schema):
    id: int
    title: str


class PostDetails(Schema):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    published: Optional[datetime] = None
    author_id: int
    slug: str
    series: Optional[SeriesSummary] = None


class PostSummary(Schema):
    id: int
    title: str
    published: Optional[datetime] = None
    slug: str


class ValidationErrorResponse(Schema):
    detail: str


class FileDetails(Schema):
    id: int
    name: str
    content_type: str
    charset: Optional[str]
    size: int
    location: str
    created_at: datetime
    posts: List[PostSummary]
    visibility: str


class FileMetadata(Schema):
    posts: Optional[List[int]] = None
    visibility: str = "public"


class FileMutateMetadata(Schema):
    posts: Optional[List[int]] = None


class AuthorSummary(Schema):
    id: int
    username: str
    name: Optional[str] = Field(None, description="The author's name")
    url: Optional[str] = Field(
        None,
        description="The URL of a site owned by the author. It could be a blog, micro-blog, Twitter account, etc.",
    )
    avatar: Optional[str] = Field(
        None,
        description="The URL for an image for the author. Should be square and relatively large — such as 512 x 512 pixels.",
    )


class CommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    children: List["CommentList"]
    created_at: datetime
    updated_at: datetime
    post: PostDetails


class AdminChildCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    children: Optional[List["AdminCommentList"]] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminParentCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    parent: Optional["AdminParentCommentList"] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminCommentList(Schema):
    id: int
    author: AuthorSummary
    content: str
    post: PostDetails
    children: Optional[List["AdminChildCommentList"]] = None
    parent: Optional["AdminParentCommentList"] = None
    visible: bool
    created_at: datetime
    updated_at: datetime
    reviewed: bool
    note: Optional[str] = None


class AdminCommentUpdate(Schema):
    visible: Optional[bool] = None
    note: Optional[str] = None
    reviewed: bool


class CommentMutate(Schema):
    content: str


class CommentCreate(Schema):
    content: str
    parent_id: Optional[int] = None
    post_id: int


class OrphanedFileDetails(Schema):
    name: str
    size: int
    content_type: str
    location: str
    last_modified: Optional[datetime]
    visibility: str


class OrphanedFiles(Schema):
    public: List[OrphanedFileDetails]
    private: List[OrphanedFileDetails]


# JSON Feed Schemas
class Hub(Schema):
    type: str = Field(..., description="The type of the hub.")
    url: str = Field(..., description="The URL of the hub.")


class Attachment(Schema):
    url: str = Field(..., description="The URL of the attachment")
    mime_type: str = Field(..., description="The MIME type of the attachment")
    title: Optional[str] = Field(None, description="A name for the attachment")
    size_in_bytes: Optional[int] = Field(None, description="The size of the attachment in bytes")
    duration_in_seconds: Optional[int] = Field(
        None, description="The duration of the attachment in seconds, if it's audio or video"
    )


class FeedItem(Schema):
    id: str = Field(
        ...,
        description="Unique for that item for that feed over time. If an item is ever updated, the id should be unchanged. New items should never use a previously-used id.",
    )
    url: Optional[str] = Field(
        None, description="The URL of the resource described by the item. It's the permalink."
    )
    external_url: Optional[str] = Field(
        None, description="The URL of a page elsewhere. This is especially useful for linkblogs."
    )
    title: Optional[str] = Field(
        None,
        description="Plain text title of the item. Microblog items in particular may omit titles.",
    )
    content_html: Optional[str] = Field(
        None,
        description="The HTML content of the item. If content_html includes any HTML, it MUST be encoded as valid HTML.",
    )
    content_text: Optional[str] = Field(
        None,
        description="The plain text content of the item. Microblog items in particular may omit titles.",
    )
    summary: Optional[str] = Field(
        None,
        description="A plain text sentence or two describing the item. This might be presented in a timeline, for instance.",
    )
    image: Optional[str] = Field(
        None,
        description="The URL of the main image for the item. This image may also appear in the content_html.",
    )
    banner_image: Optional[str] = Field(
        None,
        description="The URL of an image to use as a banner. Some feed readers may choose to display this banner image at the top of the feed.",
    )
    date_published: Optional[datetime] = Field(
        None, description="The date the item was published in RFC 3339 format."
    )
    date_modified: Optional[datetime] = Field(
        None, description="The date the item was modified in RFC 3339 format."
    )
    authors: Optional[List[AuthorSummary]] = Field(None, description="The authors of the item.")
    tags: Optional[List[str]] = Field(
        None,
        description="An array of tags or categories. These can be used to categorize items across feeds.",
    )
    language: Optional[str] = Field(
        None, description="The primary language for the item in the format specified in RFC 5646."
    )
    attachments: Optional[List[Attachment]] = Field(
        None, description="An array of attachments, such as audio or video files."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "2347259",
                "url": "https://example.org/2347259",
                "content_text": "Hello World!",
                "date_published": "2023-04-20T14:22:00-07:00",
            }
        }


class FeedAuthorSchema(Schema):
    name: Optional[str] = None
    url: Optional[str] = None
    avatar: Optional[str] = None


class JSONFeed(Schema):
    version: str = Field(
        "https://jsonfeed.org/version/1.1",
        description="The URL of the version of the format the feed uses. Must be https://jsonfeed.org/version/1.1",
    )
    title: str = Field(
        ...,
        description="The name of the feed, which will often correspond to the name of the website.",
    )
    home_page_url: Optional[str] = Field(
        None,
        description="The URL of the resource that the feed describes. This should be an HTML page that corresponds to the feed.",
    )
    feed_url: Optional[str] = Field(
        None, description="The URL of the feed, and serves as the unique identifier for the feed."
    )
    description: Optional[str] = Field(
        None, description="Provides more detail, beyond the title, on what the feed is about."
    )
    user_comment: Optional[str] = Field(
        None,
        description="A description of the purpose of the feed. This is for the use of people looking at the raw JSON, and should be ignored by feed readers.",
    )
    next_url: Optional[str] = Field(
        None,
        description="The URL of a feed that provides the next n items, where n is determined by the publisher.",
    )
    icon: Optional[str] = Field(
        None,
        description="The URL of an image for the feed suitable to be used in a timeline, much the way an avatar might be used. Should be square and relatively large — such as 512 x 512 pixels.",
    )
    favicon: Optional[str] = Field(
        None,
        description="The URL of an image for the feed suitable to be used in a source list. Should be square and relatively small, but not smaller than 64 x 64 pixels.",
    )
    authors: Optional[List[FeedAuthorSchema]] = Field(None, description="The authors of the feed.")
    language: Optional[str] = Field(
        None, description="The primary language for the feed in the format specified in RFC 5646."
    )
    expired: Optional[bool] = Field(
        None,
        description="Says whether or not the feed is finished — that is, whether or not it will ever update again.",
    )
    hubs: Optional[List[Hub]] = Field(
        None,
        description="Endpoints that can be used to subscribe to real-time notifications from the publisher of this feed.",
    )
    items: List[FeedItem] = Field(
        ..., description="The list of items in the feed. Must have at least one item."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "version": "https://jsonfeed.org/version/1.1",
                "title": "My Example Feed",
                "home_page_url": "https://example.org/",
                "feed_url": "https://example.org/feed.json",
                "items": [
                    {
                        "id": "2",
                        "content_text": "This is a second item.",
                        "url": "https://example.org/second-item",
                    },
                    {
                        "id": "1",
                        "content_html": "<p>Hello, world!</p>",
                        "url": "https://example.org/initial-post",
                    },
                ],
            }
        }


# SERIES SCHEMAS
class SeriesBase(Schema):
    title: str = Field(..., max_length=200)
    slug: str = Field(
        ...,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-friendly identifier. Will be auto-generated from title if not provided.",
    )
    description: Optional[str] = None


class SeriesCreate(SeriesBase):
    pass


class SeriesUpdate(
    Schema
):  # Using Schema directly as all fields are optional for PATCH-like behavior
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = None


class SeriesPublic(SeriesBase):
    id: int
    created_at: datetime
    updated_at: datetime
    post_count: int = 0  # This will typically be annotated in the query


class PostSummaryForSeries(Schema):
    id: int
    title: str
    slug: str
    year: Optional[int] = None  # To help construct URLs, derived from published_at
    published_at: Optional[datetime] = None


class SeriesDetailPublic(SeriesPublic):
    posts: List[PostSummaryForSeries] = []


class SeriesListResponse(Schema):
    items: List[SeriesPublic]
    count: int


# POST SCHEMAS (Updated)
class PostBase(Schema):
    title: str = Field(..., max_length=200)
    # slug: str = Field(..., max_length=200) # Slug is handled in PostCreate and PostPublic explicitly
    content: str
    published_at: Optional[datetime] = None
    series_id: Optional[int] = Field(None, description="ID of the series this post belongs to")


class PostCreate(PostBase):
    slug: Optional[str] = Field(
        None,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-friendly identifier. Will be auto-generated from title if not provided and not present.",
    )


class PostUpdate(
    Schema
):  # Using Schema directly as all fields are optional for PATCH-like behavior
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    series_id: Optional[int] = Field(None, description="ID of the series this post belongs to")
    # tags: Optional[List[str]] = Field(None, description="List of tag names") # Assuming tags might be handled like this


class PostPublic(PostBase):
    id: int
    slug: str  # Slug is mandatory in public representation
    author: UserPublic  # Now UserPublic should be defined
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0  # Typically annotated
    series: Optional[SeriesPublic] = Field(
        None, description="Full details of the series this post belongs to"
    )
    # tags: List[TagPublic] = [] # Assuming TagPublic is defined elsewhere


class PostListPublic(PostPublic):
    # For list views, content might be truncated or have a summary
    # content: Optional[str] = None # Override if full content not needed for lists
    pass  # Inherits from PostPublic, can be specialized if needed (e.g. truncated content)


class PostListResponse(Schema):
    items: List[PostListPublic]
    count: int
    offset: Optional[int] = None  # For pagination metadata
    limit: Optional[int] = None  # For pagination metadata


# Ensure UserPublic, FilePublic, CommentPublic, TagPublic are defined as needed above or are already present.
# For example:


class ShareCodeSchema(Schema):
    id: int
    code: str
    note: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


class ShareCodeCreate(Schema):
    note: Optional[str] = None
    expires_at: Optional[datetime] = None
