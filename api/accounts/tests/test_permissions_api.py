import json
from typing import Any, Dict, List

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test.client import Client

from accounts.models import User


@pytest.fixture
def test_permission() -> Permission:
    """Create a test permission."""
    content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.create(
        name="Can test user",
        codename="can_test_user",
        content_type=content_type,
    )
    return permission


@pytest.fixture
def test_content_type() -> ContentType:
    """Get a test content type."""
    return ContentType.objects.get_for_model(User)


@pytest.mark.django_db
class TestListPermissionsEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_permissions_staff(
        self, client: Client, auth_token: str, test_permission: Permission
    ) -> None:
        """Test that staff users can list all permissions."""
        response: HttpResponse = client.get(
            "/api/permissions/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert "items" in data
        assert len(data["items"]) >= 1

        permission_names: List[str] = [perm["name"] for perm in data["items"]]
        assert "Can test user" in permission_names

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_list_permissions_non_staff(self, client: Client, auth_token: str) -> None:
        """Test that non-staff users cannot list permissions."""
        response: HttpResponse = client.get(
            "/api/permissions/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_list_permissions_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot list permissions."""
        response: HttpResponse = client.get("/api/permissions/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestCreatePermissionEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_permission_staff(
        self, client: Client, auth_token: str, test_content_type: ContentType
    ) -> None:
        """Test that staff users can create permissions."""
        permission_data: Dict[str, Any] = {
            "name": "Can do something",
            "codename": "can_do_something",
            "content_type": {
                "id": test_content_type.id,
                "app_label": test_content_type.app_label,
                "model": test_content_type.model,
                "name": test_content_type.name,
                "app_labeled_name": f"{test_content_type.app_label}.{test_content_type.model}",
            },
        }

        response: HttpResponse = client.post(
            "/api/permissions/",
            data=json.dumps(permission_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["name"] == "Can do something"
        assert data["codename"] == "can_do_something"
        assert data["content_type"]["id"] == test_content_type.id

        # Verify the permission was created
        assert Permission.objects.filter(codename="can_do_something").exists()
        new_permission = Permission.objects.get(codename="can_do_something")
        assert new_permission.name == "Can do something"
        assert new_permission.content_type == test_content_type

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_create_permission_non_staff(
        self, client: Client, auth_token: str, test_content_type: ContentType
    ) -> None:
        """Test that non-staff users cannot create permissions."""
        permission_data: Dict[str, Any] = {
            "name": "Can do something",
            "codename": "can_do_something",
            "content_type": {
                "id": test_content_type.id,
                "app_label": test_content_type.app_label,
                "model": test_content_type.model,
                "name": test_content_type.name,
                "app_labeled_name": f"{test_content_type.app_label}.{test_content_type.model}",
            },
        }

        response: HttpResponse = client.post(
            "/api/permissions/",
            data=json.dumps(permission_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_create_permission_unauthenticated(
        self, client: Client, test_content_type: ContentType
    ) -> None:
        """Test that unauthenticated users cannot create permissions."""
        permission_data: Dict[str, Any] = {
            "name": "Can do something",
            "codename": "can_do_something",
            "content_type": {
                "id": test_content_type.id,
                "app_label": test_content_type.app_label,
                "model": test_content_type.model,
                "name": test_content_type.name,
                "app_labeled_name": f"{test_content_type.app_label}.{test_content_type.model}",
            },
        }

        response: HttpResponse = client.post(
            "/api/permissions/",
            data=json.dumps(permission_data),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdatePermissionEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_permission_staff(
        self,
        client: Client,
        auth_token: str,
        test_permission: Permission,
        test_content_type: ContentType,
    ) -> None:
        """Test that staff users can update permissions."""
        update_data: Dict[str, Any] = {
            "name": "Updated permission",
            "codename": "updated_permission",
            "content_type": {
                "id": test_content_type.id,
                "app_label": test_content_type.app_label,
                "model": test_content_type.model,
                "name": test_content_type.name,
                "app_labeled_name": f"{test_content_type.app_label}.{test_content_type.model}",
            },
        }

        response: HttpResponse = client.put(
            f"/api/permissions/{test_permission.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["name"] == "Updated permission"
        assert data["codename"] == "updated_permission"
        assert data["content_type"]["id"] == test_content_type.id

        # Verify the database was updated
        test_permission.refresh_from_db()
        assert test_permission.name == "Updated permission"
        assert test_permission.codename == "updated_permission"
        assert test_permission.content_type == test_content_type

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_permission_not_found(
        self, client: Client, auth_token: str, test_content_type: ContentType
    ) -> None:
        """Test updating a non-existent permission."""
        update_data: Dict[str, Any] = {
            "name": "Updated permission",
            "codename": "updated_permission",
            "content_type": {
                "id": test_content_type.id,
                "app_label": test_content_type.app_label,
                "model": test_content_type.model,
                "name": test_content_type.name,
                "app_labeled_name": f"{test_content_type.app_label}.{test_content_type.model}",
            },
        }

        response: HttpResponse = client.put(
            "/api/permissions/9999",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_permission_non_staff(
        self, client: Client, auth_token: str, test_permission: Permission
    ) -> None:
        """Test that non-staff users cannot update permissions."""
        update_data: Dict[str, Any] = {"name": "Updated permission"}

        response: HttpResponse = client.put(
            f"/api/permissions/{test_permission.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_update_permission_unauthenticated(
        self, client: Client, test_permission: Permission
    ) -> None:
        """Test that unauthenticated users cannot update permissions."""
        update_data: Dict[str, Any] = {"name": "Updated permission"}

        response: HttpResponse = client.put(
            f"/api/permissions/{test_permission.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 403
