from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import Field


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


class FeedAuthorSchema(Schema):
    name: Optional[str] = None
    url: Optional[str] = None
    avatar: Optional[str] = None


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
    authors: Optional[List[FeedAuthorSchema]] = Field(None, description="The authors of the item.")
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
