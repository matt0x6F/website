import pytest
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
