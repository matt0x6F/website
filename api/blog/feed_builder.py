from typing import List

from .schemas import Author, FeedItem, Hub, JSONFeed


class FeedBuilder:
    """Builder class to help construct JSONFeed objects in a fluent manner."""

    def __init__(self, title: str):
        """Initialize a new FeedBuilder with required title."""
        self._data = {"version": "https://jsonfeed.org/version/1.1", "title": title, "items": []}

    def with_home_page_url(self, url: str) -> "FeedBuilder":
        """Set the home page URL."""
        self._data["home_page_url"] = url
        return self

    def with_feed_url(self, url: str) -> "FeedBuilder":
        """Set the feed URL."""
        self._data["feed_url"] = url
        return self

    def with_description(self, description: str) -> "FeedBuilder":
        """Set the feed description."""
        self._data["description"] = description
        return self

    def with_user_comment(self, comment: str) -> "FeedBuilder":
        """Set the user comment."""
        self._data["user_comment"] = comment
        return self

    def with_next_url(self, url: str) -> "FeedBuilder":
        """Set the next URL for pagination."""
        self._data["next_url"] = url
        return self

    def with_icon(self, url: str) -> "FeedBuilder":
        """Set the icon URL."""
        self._data["icon"] = url
        return self

    def with_favicon(self, url: str) -> "FeedBuilder":
        """Set the favicon URL."""
        self._data["favicon"] = url
        return self

    def with_authors(self, authors: List[Author]) -> "FeedBuilder":
        """Set the feed authors."""
        self._data["authors"] = authors
        return self

    def with_language(self, language: str) -> "FeedBuilder":
        """Set the feed language."""
        self._data["language"] = language
        return self

    def set_expired(self, expired: bool = True) -> "FeedBuilder":
        """Set whether the feed is expired."""
        self._data["expired"] = expired
        return self

    def with_hubs(self, hubs: List[Hub]) -> "FeedBuilder":
        """Set the feed hubs."""
        self._data["hubs"] = hubs
        return self

    def add_item(self, item: FeedItem) -> "FeedBuilder":
        """Add a feed item to the items list."""
        if "items" not in self._data:
            self._data["items"] = []
        self._data["items"].append(item)
        return self

    def build(self) -> JSONFeed:
        """Build and return the JSONFeed object."""
        return JSONFeed(**self._data)
