import json

import pytest
from django.test.client import Client

from blog.models import Comment


@pytest.mark.django_db
class TestCommentsAPI:
    def test_list_comments_unauthenticated(self, client: Client, post, comment):
        response = client.get(f"/api/comments/?post_id={post.id}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_create_comment_authenticated(self, client: Client, auth_token: str, post):
        payload = {"content": "New comment", "post_id": post.id}
        response = client.post(
            "/api/comments/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert data["content"] == "New comment"
        assert data["post"]["id"] == post.id

    def test_create_comment_unauthenticated(self, client: Client, post):
        payload = {"content": "Should fail", "post_id": post.id}
        response = client.post(
            "/api/comments/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 401 or response.status_code == 403

    def test_get_comment_by_id(self, client: Client, comment):
        response = client.get(f"/api/comments/{comment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == comment.id
        assert data["content"] == comment.content

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_comment_author(self, client: Client, auth_token: str, comment):
        payload = {"content": "Updated comment"}
        response = client.put(
            f"/api/comments/{comment.id}",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.content == "Updated comment"

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_delete_comment_author(self, client: Client, auth_token: str, comment):
        response = client.delete(
            f"/api/comments/{comment.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200 or response.status_code == 204
        assert not Comment.objects.filter(id=comment.id).exists()
