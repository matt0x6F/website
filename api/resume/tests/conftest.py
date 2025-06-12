from datetime import date

import pytest
from ninja_jwt.tokens import RefreshToken

from accounts.models import User
from resume.models import Experience, Proficiency, Resume


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
def proficiency(db):
    """Create a test proficiency"""
    return Proficiency.objects.create(category="Programming", items=["Python", "JavaScript"])


@pytest.fixture
def experience(db):
    """Create a test experience"""
    return Experience.objects.create(
        title="Senior Developer",
        company="Test Company",
        start_date=date(2020, 1, 1),
        end_date=date(2023, 1, 1),
        is_current=False,
        achievements="- Led team of 5 developers\n- Implemented CI/CD pipeline",
    )


@pytest.fixture
def current_experience(db):
    """Create a test current experience"""
    return Experience.objects.create(
        title="Lead Developer",
        company="Current Company",
        start_date=date(2023, 1, 1),
        is_current=True,
        achievements="Leading team",
    )


@pytest.fixture
def resume_data():
    return {
        "name": "Test User",
        "github_url": "https://github.com/testuser",
        "website_url": "https://testuser.com",
        "bio": "Test bio",
        "proficiencies": [
            {"category": "Programming", "items": ["Python", "JavaScript"]},
            {"category": "Frameworks", "items": ["Django", "React"]},
        ],
        "experiences": [
            {
                "title": "Senior Developer",
                "company": "Test Company",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
                "is_current": False,
                "achievements": "- Led team of 5 developers\n- Implemented CI/CD pipeline",
            },
            {
                "title": "Lead Developer",
                "company": "Current Company",
                "start_date": "2023-01-01",
                "is_current": True,
                "achievements": "- Leading team of 10 developers\n- Architecting new systems",
            },
        ],
    }


@pytest.fixture
def resume(db, resume_data):
    resume = Resume.objects.create(
        name=resume_data["name"],
        github_url=resume_data["github_url"],
        website_url=resume_data["website_url"],
        bio=resume_data["bio"],
    )

    for prof in resume_data["proficiencies"]:
        proficiency = Proficiency.objects.create(category=prof["category"], items=prof["items"])
        resume.proficiencies.add(proficiency)

    for exp in resume_data["experiences"]:
        experience = Experience.objects.create(
            title=exp["title"],
            company=exp["company"],
            start_date=exp["start_date"],
            end_date=exp.get("end_date"),
            is_current=exp["is_current"],
            achievements=exp["achievements"],
        )
        resume.experiences.add(experience)

    return resume
