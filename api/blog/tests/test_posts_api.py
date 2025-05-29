import json

import pytest
from django.test.client import Client

from blog.models import Post


@pytest.mark.django_db
class TestPostsAPI:
    def test_list_posts_unauthenticated(self, client: Client, post):
        response = client.get("/api/posts/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_post_staff(self, client: Client, auth_token: str, superuser):
        payload = {
            "title": "New Post",
            "content": "Some content",
            "series_id": None,
        }
        response = client.post(
            "/api/posts/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Post"
        assert data["content"] == "Some content"

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_create_post_non_staff_forbidden(self, client: Client, auth_token: str):
        payload = {"title": "Should Fail", "content": "Nope"}
        response = client.post(
            "/api/posts/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 403 or response.status_code == 400

    def test_get_post_by_id(self, client: Client, post):
        response = client.get(f"/api/posts/{post.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post.id
        assert data["title"] == post.title

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_post_staff(self, client: Client, auth_token: str, post, superuser):
        # Make the post author the superuser for update
        post.author = superuser
        post.save()
        payload = {"title": "Updated Title"}
        response = client.put(
            f"/api/posts/{post.id}",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "Updated Title"

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_post_staff(self, client: Client, auth_token: str, post, superuser):
        # Make the post author the superuser for deletion
        post.author = superuser
        post.save()
        response = client.delete(
            f"/api/posts/{post.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 204 or response.status_code == 200
        assert not Post.objects.filter(id=post.id).exists()

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_drafts_ordered_by_updated_at_desc(
        self, client: Client, auth_token: str, superuser, series
    ):
        # Create three draft posts with different updated_at
        import datetime

        from django.utils import timezone

        from blog.models import Post

        now = timezone.now()
        post1 = Post.objects.create(
            title="Draft 1",
            slug="draft-1",
            author=superuser,
            content="Draft 1 content",
            published_at=None,
            series=series,
        )
        post2 = Post.objects.create(
            title="Draft 2",
            slug="draft-2",
            author=superuser,
            content="Draft 2 content",
            published_at=None,
            series=series,
        )
        post3 = Post.objects.create(
            title="Draft 3",
            slug="draft-3",
            author=superuser,
            content="Draft 3 content",
            published_at=None,
            series=series,
        )
        # Manually set updated_at
        Post.objects.filter(id=post1.id).update(updated_at=now - datetime.timedelta(days=2))
        Post.objects.filter(id=post2.id).update(updated_at=now - datetime.timedelta(days=1))
        Post.objects.filter(id=post3.id).update(updated_at=now)

        response = client.get(
            "/api/posts/?drafts=true",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()
        items = data["items"] if "items" in data else data
        # Should be ordered by -updated_at (most recent first)
        assert [item["title"] for item in items] == ["Draft 3", "Draft 2", "Draft 1"]

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_drafts_ordered_by_updated_at_asc(
        self, client: Client, auth_token: str, superuser, series
    ):
        import datetime

        from django.utils import timezone

        from blog.models import Post

        now = timezone.now()
        post1 = Post.objects.create(
            title="Draft A",
            slug="draft-a",
            author=superuser,
            content="Draft A content",
            published_at=None,
            series=series,
        )
        post2 = Post.objects.create(
            title="Draft B",
            slug="draft-b",
            author=superuser,
            content="Draft B content",
            published_at=None,
            series=series,
        )
        post3 = Post.objects.create(
            title="Draft C",
            slug="draft-c",
            author=superuser,
            content="Draft C content",
            published_at=None,
            series=series,
        )
        # Manually set updated_at
        Post.objects.filter(id=post1.id).update(updated_at=now - datetime.timedelta(days=2))
        Post.objects.filter(id=post2.id).update(updated_at=now - datetime.timedelta(days=1))
        Post.objects.filter(id=post3.id).update(updated_at=now)

        response = client.get(
            "/api/posts/?drafts=true&order=updated_at",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()
        items = data["items"] if "items" in data else data
        # Should be ordered by updated_at (oldest first)
        assert [item["title"] for item in items] == ["Draft A", "Draft B", "Draft C"]
