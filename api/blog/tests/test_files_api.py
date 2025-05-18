import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client

from blog.models import File


@pytest.mark.django_db
class TestFilesAPI:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_files_staff(self, client: Client, auth_token: str):
        response = client.get(
            "/api/files/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_file_staff(self, client: Client, auth_token: str):
        file_data = SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
        response = client.post(
            "/api/files/",
            data={
                "metadata": json.dumps({"visibility": "public", "posts": []}),
                "upload": file_data,
            },
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"].startswith("test") and data["name"].endswith(".txt")
        assert data["visibility"] == "public"

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_get_file_by_id_staff(self, client: Client, auth_token: str, post):
        # Create a file first
        file_obj = File.objects.create(
            name="test.txt",
            content_type="text/plain",
            charset="utf-8",
            visibility="public",
            size=11,
            location="/fake/path/test.txt",
        )
        file_obj.posts.add(post)
        response = client.get(
            f"/api/files/{file_obj.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == file_obj.id
        assert data["name"] == "test.txt"
