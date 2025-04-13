import json
from typing import Any, Dict, List

import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test.client import Client

from accounts.models import User


@pytest.fixture
def test_group() -> Group:
    """Create a test group."""
    group = Group.objects.create(name="test_group")
    return group


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


@pytest.mark.django_db
class TestListGroupsEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_groups_staff(self, client: Client, auth_token: str, test_group: Group) -> None:
        """Test that staff users can list all groups."""
        response: HttpResponse = client.get(
            "/api/groups/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert "items" in data
        assert len(data["items"]) >= 1

        group_names: List[str] = [group["name"] for group in data["items"]]
        assert "test_group" in group_names

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_list_groups_non_staff(self, client: Client, auth_token: str) -> None:
        """Test that non-staff users cannot list groups."""
        response: HttpResponse = client.get(
            "/api/groups/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_list_groups_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot list groups."""
        response: HttpResponse = client.get("/api/groups/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestCreateGroupEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_create_group_staff(
        self, client: Client, auth_token: str, test_permission: Permission
    ) -> None:
        """Test that staff users can create groups."""
        group_data: Dict[str, Any] = {
            "name": "new_group",
            "permissions": [test_permission.id],
        }

        response: HttpResponse = client.post(
            "/api/groups/",
            data=json.dumps(group_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["name"] == "new_group"
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]["id"] == test_permission.id

        # Verify the group was created
        assert Group.objects.filter(name="new_group").exists()
        new_group = Group.objects.get(name="new_group")
        assert list(new_group.permissions.all()) == [test_permission]

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_create_group_non_staff(self, client: Client, auth_token: str) -> None:
        """Test that non-staff users cannot create groups."""
        group_data: Dict[str, Any] = {"name": "new_group"}

        response: HttpResponse = client.post(
            "/api/groups/",
            data=json.dumps(group_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_create_group_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot create groups."""
        group_data: Dict[str, Any] = {"name": "new_group"}

        response: HttpResponse = client.post(
            "/api/groups/",
            data=json.dumps(group_data),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdateGroupEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_group_staff(
        self, client: Client, auth_token: str, test_group: Group, test_permission: Permission
    ) -> None:
        """Test that staff users can update groups."""
        update_data: Dict[str, Any] = {
            "name": "updated_group",
            "permissions": [test_permission.id],
        }

        response: HttpResponse = client.put(
            f"/api/groups/{test_group.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["name"] == "updated_group"
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]["id"] == test_permission.id

        # Verify the database was updated
        test_group.refresh_from_db()
        assert test_group.name == "updated_group"
        assert list(test_group.permissions.all()) == [test_permission]

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_group_not_found(self, client: Client, auth_token: str) -> None:
        """Test updating a non-existent group."""
        update_data: Dict[str, Any] = {"name": "updated_group"}

        response: HttpResponse = client.put(
            "/api/groups/9999",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_group_non_staff(
        self, client: Client, auth_token: str, test_group: Group
    ) -> None:
        """Test that non-staff users cannot update groups."""
        update_data: Dict[str, Any] = {"name": "updated_group"}

        response: HttpResponse = client.put(
            f"/api/groups/{test_group.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_update_group_unauthenticated(self, client: Client, test_group: Group) -> None:
        """Test that unauthenticated users cannot update groups."""
        update_data: Dict[str, Any] = {"name": "updated_group"}

        response: HttpResponse = client.put(
            f"/api/groups/{test_group.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestDeleteGroupEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_group_staff(self, client: Client, auth_token: str, test_group: Group) -> None:
        """Test that staff users can delete groups."""
        response: HttpResponse = client.delete(
            f"/api/groups/{test_group.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200

        # Verify the group was deleted
        assert not Group.objects.filter(name="test_group").exists()

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_group_not_found(self, client: Client, auth_token: str) -> None:
        """Test deleting a non-existent group."""
        response: HttpResponse = client.delete(
            "/api/groups/9999",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_delete_group_non_staff(
        self, client: Client, auth_token: str, test_group: Group
    ) -> None:
        """Test that non-staff users cannot delete groups."""
        response: HttpResponse = client.delete(
            f"/api/groups/{test_group.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_delete_group_unauthenticated(self, client: Client, test_group: Group) -> None:
        """Test that unauthenticated users cannot delete groups."""
        response: HttpResponse = client.delete(f"/api/groups/{test_group.id}")
        assert response.status_code == 403
