from django.http import HttpRequest
from django.utils import timezone
from ninja import Router
from ninja.responses import Response

from auth.middleware import JWTAuth
from blog.feed_builder import FeedBuilder
from blog.schema.feed import FeedAuthorSchema, FeedItem, JSONFeed

from ..models import Post

feed_router = Router()


@feed_router.get(
    "/",
    auth=JWTAuth(None, True),
    response={200: JSONFeed},
    tags=["feed"],
    operation_id="getFeed",
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
            f"https://ooo-yay.com/api/feed/?limit={limit}&offset={offset + limit}"
        )

    return Response(builder.build(), content_type="application/feed+json")
