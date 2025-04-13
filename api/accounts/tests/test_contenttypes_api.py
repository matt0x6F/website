import json
from typing import Any, Dict, List

import pytest
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test.client import Client

from accounts.models import User


@pytest.mark.django_db
class TestListContentTypesEndpoint:
    def test_list_content_types_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot list content types."""
        response: HttpResponse = client.get("/api/contenttypes/")
        assert response.status_code == 403

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_list_content_types_authenticated_non_staff(
        self, client: Client, auth_token: str
    ) -> None:
        """Test that non-staff users cannot list content types."""
        response: HttpResponse = client.get(
            "/api/contenttypes/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 403

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_content_types_staff(self, client: Client, auth_token: str) -> None:
        """Test that staff users can list content types."""
        # Get the User content type as a reference
        user_ct = ContentType.objects.get_for_model(User)

        response: HttpResponse = client.get(
            "/api/contenttypes/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: List[Dict[str, Any]] = json.loads(response.content)

        # Verify the response structure
        assert isinstance(data, list)
        assert len(data) > 0  # Should have at least the User content type

        # Find the User content type in the response
        user_ct_data = next((ct for ct in data if ct["id"] == user_ct.id), None)
        assert user_ct_data is not None
        assert user_ct_data["app_label"] == user_ct.app_label
        assert user_ct_data["model"] == user_ct.model
        assert user_ct_data["name"] == user_ct.name
        assert user_ct_data["app_labeled_name"] == f"{user_ct.app_label}.{user_ct.model}"

        # Verify the response is ordered by app_label and model
        sorted_data = sorted(data, key=lambda x: (x["app_label"], x["model"]))
        assert data == sorted_data
