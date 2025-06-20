import structlog

# from config.utils.permissions import StaffPermission # Commented out problematic import
from django.http import HttpRequest
from django.utils import timezone
from ninja import Router
from ninja.responses import Response
from pydantic import BaseModel

from auth.middleware import JWTAuth
from blog.feed_builder import FeedBuilder
from blog.models import Post
from blog.schema import (
    FeedAuthorSchema,
    FeedItem,
    JSONFeed,
)

logger = structlog.get_logger(__name__)

posts_router = Router()
series_router = Router()


class FeedAuthor(BaseModel):
    name: str
    url: str


#
# Feed
#


#
# Series
#


@series_router.get(
    "/",
    auth=JWTAuth(None, True),
    response={200: JSONFeed},
    tags=["series"],
)
def series(request: HttpRequest, limit: int = 10, offset: int = 0):
    builder = (
        FeedBuilder(title="ooo-yay series")
        .with_authors([FeedAuthorSchema(name="Matt Ouille", url="https://ooo-yay.com")])
        .with_description("Latest series from @ooo-yay")
        .with_icon("https://ooo-yay.com/logo.svg")
        .with_favicon("https://ooo-yay.com/logo.svg")
        .with_feed_url("https://ooo-yay.com/api/series/")
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
            f"https://ooo-yay.com/series.json?limit={limit}&offset={offset + limit}"
        )

    return Response(builder.build(), content_type="application/feed+json")
