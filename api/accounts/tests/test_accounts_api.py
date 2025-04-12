import json
from typing import Any, Dict, List

import pytest
from django.http import HttpResponse
from django.test.client import Client
from ninja_jwt.tokens import RefreshToken

from accounts.models import User


@pytest.fixture
def superuser() -> User:
    """Create a superuser for testing."""
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpassword",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def regular_user() -> User:
    """Create a regular authenticated user for testing."""
    user = User.objects.create_user(
        username="user",
        email="user@example.com",
        password="userpassword",
    )
    return user


@pytest.fixture
def auth_token(request: pytest.FixtureRequest) -> str:
    """Generate JWT token for the specified user."""
    user = request.getfixturevalue(request.param)
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
class TestWhoAmIEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser", "regular_user"], indirect=True)
    def test_whoami_authenticated(self, client: Client, auth_token: str) -> None:
        """Test that authenticated users can access their own details."""
        response: HttpResponse = client.get(
            "/api/accounts/me",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert "username" in data
        assert "email" in data

    def test_whoami_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot access the whoami endpoint."""
        response: HttpResponse = client.get("/api/accounts/me")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdateSelfEndpoint:
    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_self(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that users can update their own details."""
        update_data: Dict[str, str] = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.com",
            "avatar_link": "https://example.com/avatar.jpg",
        }

        response: HttpResponse = client.put(
            "/api/accounts/me",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "User"
        assert data["email"] == "updated@example.com"
        assert data["avatar_link"] == "https://example.com/avatar.jpg"

        # Verify the database was updated
        regular_user.refresh_from_db()
        assert regular_user.first_name == "Updated"
        assert regular_user.last_name == "User"
        assert regular_user.email == "updated@example.com"
        assert regular_user.avatar_link == "https://example.com/avatar.jpg"

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_password(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that users can update their password."""
        update_data: Dict[str, str] = {
            "old_password": "userpassword",
            "new_password": "newuserpassword",
        }

        response: HttpResponse = client.put(
            "/api/accounts/me",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200

        # Verify the password was updated
        regular_user.refresh_from_db()
        assert regular_user.check_password("newuserpassword")

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_username(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that users can update their username."""
        update_data: Dict[str, str] = {
            "username": "updated_user",
        }

        response: HttpResponse = client.put(
            "/api/accounts/me",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["username"] == "updated_user"

        # Verify the database was updated
        regular_user.refresh_from_db()
        assert regular_user.username == "updated_user"

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_password_wrong_old_password(self, client: Client, auth_token: str) -> None:
        """Test that users cannot update their password with wrong old password."""
        update_data: Dict[str, str] = {
            "old_password": "wrongpassword",
            "new_password": "newuserpassword",
        }

        response: HttpResponse = client.put(
            "/api/accounts/me",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_update_self_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot update user details."""
        update_data: Dict[str, str] = {"first_name": "Updated"}

        response: HttpResponse = client.put(
            "/api/accounts/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestDeleteSelfEndpoint:
    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_delete_self(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that users can delete their own account."""
        response: HttpResponse = client.delete(
            "/api/accounts/me",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200

        # Verify the user was deleted
        assert not User.objects.filter(username="user").exists()

    def test_delete_self_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot delete accounts."""
        response: HttpResponse = client.delete("/api/accounts/me")
        assert response.status_code == 403


@pytest.mark.django_db
class TestSignUpEndpoint:
    def test_sign_up(self, client: Client) -> None:
        """Test that new users can sign up."""
        new_user_data: Dict[str, str] = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newuserpassword",
            "first_name": "New",
            "last_name": "User",
        }

        response: HttpResponse = client.post(
            "/api/accounts/sign_up",
            data=json.dumps(new_user_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"

        # Verify the user was created
        assert User.objects.filter(username="newuser").exists()
        new_user = User.objects.get(username="newuser")
        assert new_user.check_password("newuserpassword")

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_sign_up_authenticated(self, client: Client, auth_token: str) -> None:
        """Test that authenticated users cannot sign up new accounts."""
        new_user_data: Dict[str, str] = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newuserpassword",
        }

        response: HttpResponse = client.post(
            "/api/accounts/sign_up",
            data=json.dumps(new_user_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestListUsersEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_list_users_staff(
        self, client: Client, auth_token: str, superuser: User, regular_user: User
    ) -> None:
        """Test that staff users can list all users."""
        response: HttpResponse = client.get(
            "/api/accounts/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert "items" in data
        assert len(data["items"]) >= 2  # At least superuser and regular_user

        usernames: List[str] = [user["username"] for user in data["items"]]
        assert "admin" in usernames
        assert "user" in usernames

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_list_users_non_staff(self, client: Client, auth_token: str) -> None:
        """Test that non-staff users cannot list all users."""
        response: HttpResponse = client.get(
            "/api/accounts/",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_list_users_unauthenticated(self, client: Client) -> None:
        """Test that unauthenticated users cannot list all users."""
        response: HttpResponse = client.get("/api/accounts/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetUserEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_get_user_staff(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that staff users can get details of a specific user."""
        response: HttpResponse = client.get(
            f"/api/accounts/{regular_user.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["username"] == "user"
        assert data["email"] == "user@example.com"

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_get_user_not_found(self, client: Client, auth_token: str) -> None:
        """Test getting a non-existent user."""
        response: HttpResponse = client.get(
            "/api/accounts/9999",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_get_user_non_staff(self, client: Client, auth_token: str, superuser: User) -> None:
        """Test that non-staff users cannot get details of a specific user."""
        response: HttpResponse = client.get(
            f"/api/accounts/{superuser.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_get_user_unauthenticated(self, client: Client, regular_user: User) -> None:
        """Test that unauthenticated users cannot get user details."""
        response: HttpResponse = client.get(f"/api/accounts/{regular_user.id}")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdateUserEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_user_staff(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that staff users can update other users."""
        update_data: Dict[str, Any] = {
            "first_name": "Updated",
            "last_name": "ByAdmin",
            "email": "updated_by_admin@example.com",
            "is_active": True,
        }

        response: HttpResponse = client.put(
            f"/api/accounts/{regular_user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.content)
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "ByAdmin"
        assert data["email"] == "updated_by_admin@example.com"

        # Verify the database was updated
        regular_user.refresh_from_db()
        assert regular_user.first_name == "Updated"
        assert regular_user.last_name == "ByAdmin"
        assert regular_user.email == "updated_by_admin@example.com"

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_user_password(
        self, client: Client, auth_token: str, regular_user: User
    ) -> None:
        """Test that staff users can update other users' passwords."""
        update_data: Dict[str, str] = {
            "password": "adminsetpassword",
        }

        response: HttpResponse = client.put(
            f"/api/accounts/{regular_user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200

        # Verify the password was updated
        regular_user.refresh_from_db()
        assert regular_user.check_password("adminsetpassword")

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_user_non_staff(self, client: Client, auth_token: str, superuser: User) -> None:
        """Test that non-staff users cannot update other users."""
        update_data: Dict[str, str] = {"first_name": "Updated"}

        response: HttpResponse = client.put(
            f"/api/accounts/{superuser.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_update_user_unauthenticated(self, client: Client, regular_user: User) -> None:
        """Test that unauthenticated users cannot update users."""
        update_data: Dict[str, str] = {"first_name": "Updated"}

        response: HttpResponse = client.put(
            f"/api/accounts/{regular_user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestDeleteUserEndpoint:
    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_user_staff(self, client: Client, auth_token: str, regular_user: User) -> None:
        """Test that staff users can delete other users."""
        response: HttpResponse = client.delete(
            f"/api/accounts/{regular_user.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 200

        # Verify the user was deleted
        assert not User.objects.filter(username="user").exists()

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_delete_user_not_found(self, client: Client, auth_token: str) -> None:
        """Test deleting a non-existent user."""
        response: HttpResponse = client.delete(
            "/api/accounts/9999",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_delete_user_non_staff(self, client: Client, auth_token: str, superuser: User) -> None:
        """Test that non-staff users cannot delete other users."""
        response: HttpResponse = client.delete(
            f"/api/accounts/{superuser.id}",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )

        assert response.status_code == 403

    def test_delete_user_unauthenticated(self, client: Client, regular_user: User) -> None:
        """Test that unauthenticated users cannot delete users."""
        response: HttpResponse = client.delete(f"/api/accounts/{regular_user.id}")
        assert response.status_code == 403
