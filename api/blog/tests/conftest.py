import pytest
from django.utils import timezone
from ninja_jwt.tokens import RefreshToken

from accounts.models import User
from blog.models import Comment, Post, Series


@pytest.fixture
def superuser(db) -> User:
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpassword",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def regular_user(db) -> User:
    user = User.objects.create_user(
        username="user",
        email="user@example.com",
        password="userpassword",
    )
    return user


@pytest.fixture
def auth_token(request, db) -> str:
    user = request.getfixturevalue(request.param)
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.fixture
def series(db):
    return Series.objects.create(title="Test Series", slug="test-series")


@pytest.fixture
def post(db, regular_user, series):
    return Post.objects.create(
        title="Test Post",
        slug="test-post",
        author=regular_user,
        content="Test content",
        published_at=timezone.now(),
        series=series,
    )


@pytest.fixture
def comment(db, post, regular_user):
    return Comment.objects.create(
        post=post,
        author=regular_user,
        content="Test comment",
        visible=True,
        reviewed=False,
    )


@pytest.fixture(autouse=True)
def mock_s3_storage(monkeypatch):
    # Patch PublicStorage and PrivateStorage to use FileSystemStorage
    # monkeypatch.setattr("files.storage.PublicStorage", FileSystemStorage)
    # monkeypatch.setattr("files.storage.PrivateStorage", FileSystemStorage)
    yield
