import json

import pytest
from django.utils import timezone

from blog.models import Post, ShareCode


@pytest.mark.django_db
class TestShareCodesAPI:
    @pytest.fixture
    def draft_post(self, superuser):
        return Post.objects.create(title="Draft Post", content="Draft content", author=superuser)

    @pytest.fixture
    def another_draft_post(self, superuser):
        return Post.objects.create(title="Another Draft", content="Other content", author=superuser)

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_list_delete_sharecode(self, client, auth_token, draft_post):
        # Create
        payload = {"note": "Test code"}
        resp = client.post(
            f"/api/posts/{draft_post.id}/sharecodes",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert resp.status_code == 200
        code = resp.json()["code"]
        # List
        resp = client.get(
            f"/api/posts/{draft_post.id}/sharecodes",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert resp.status_code == 200
        codes = resp.json()
        assert any(c["code"] == code for c in codes)
        # Delete
        resp = client.delete(
            f"/api/posts/{draft_post.id}/sharecodes/{code}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert resp.status_code == 204
        assert not ShareCode.objects.filter(code=code).exists()

    def test_access_draft_with_valid_sharecode(self, client, draft_post, superuser):
        code = ShareCode.objects.create(post=draft_post, code="abc123", note="", expires_at=None)
        url = f"/api/posts/slug/{timezone.now().year}/{draft_post.slug}?sharecode=abc123"
        # Should work for unpublished post
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["id"] == draft_post.id

    def test_access_draft_with_invalid_or_expired_sharecode(self, client, draft_post):
        # Invalid code
        url = f"/api/posts/slug/{timezone.now().year}/{draft_post.slug}?sharecode=invalid"
        resp = client.get(url)
        assert resp.status_code == 404
        # Expired code
        expired = ShareCode.objects.create(
            post=draft_post, code="expired", expires_at=timezone.now() - timezone.timedelta(days=1)
        )
        url = f"/api/posts/slug/{timezone.now().year}/{draft_post.slug}?sharecode=expired"
        resp = client.get(url)
        assert resp.status_code == 404

    def test_sharecode_does_not_work_for_other_post(self, client, draft_post, another_draft_post):
        code = ShareCode.objects.create(post=draft_post, code="unique", note="")
        url = f"/api/posts/slug/{timezone.now().year}/{another_draft_post.slug}?sharecode=unique"
        resp = client.get(url)
        assert resp.status_code == 404

    def test_sharecode_invalid_after_publish(self, client, draft_post, superuser):
        code = ShareCode.objects.create(post=draft_post, code="pubcode", note="")
        # Publish the post
        draft_post.published_at = timezone.now()
        draft_post.save()
        url = f"/api/posts/slug/{draft_post.published_at.year}/{draft_post.slug}?sharecode=pubcode"
        resp = client.get(url)
        # Should be visible to all, but sharecode is not needed
        assert resp.status_code == 200
        # Remove published_at, should work only with share code
        draft_post.published_at = None
        draft_post.save()
        resp = client.get(url)
        assert resp.status_code == 200  # Should be accessible with valid share code
        # Try with invalid share code
        resp = client.get(
            f"/api/posts/slug/{timezone.now().year}/{draft_post.slug}?sharecode=invalid"
        )
        assert resp.status_code == 404
