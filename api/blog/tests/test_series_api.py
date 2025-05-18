import json

import pytest
from django.test.client import Client

from blog.models import Series


@pytest.mark.django_db
class TestSeriesAPI:
    def test_list_series_unauthenticated(self, client: Client, series):
        response = client.get("/api/series/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_series_staff(self, client: Client, auth_token: str):
        payload = {"title": "New Series", "slug": "new-series"}
        response = client.post(
            "/api/series/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert data["title"] == "New Series"

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_create_series_non_staff_forbidden(self, client: Client, auth_token: str):
        payload = {"title": "Should Fail", "slug": "fail-series"}
        response = client.post(
            "/api/series/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 403 or response.status_code == 400

    def test_get_series_by_id(self, client: Client, series):
        response = client.get(f"/api/series/{series.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == series.id
        assert data["title"] == series.title

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_series_staff(self, client: Client, auth_token: str, series):
        payload = {"title": "Updated Series"}
        response = client.put(
            f"/api/series/{series.id}",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        series.refresh_from_db()
        assert series.title == "Updated Series"

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_series_staff(self, client: Client, auth_token: str, series):
        response = client.delete(
            f"/api/series/{series.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 204 or response.status_code == 200
        assert not Series.objects.filter(id=series.id).exists()
