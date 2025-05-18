import pytest
from django.test.client import Client


@pytest.mark.django_db
class TestFeedAPI:
    def test_feed_returns_json_feed(self, client: Client, post):
        response = client.get("/api/feed/")
        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/feed+json")
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
