from datetime import date

import pytest

from resume.models import Experience, Proficiency, Resume


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
def resume(db, proficiency, experience, current_experience):
    """Create a test resume with related objects"""
    resume = Resume.objects.create(
        name="Test User",
        github_url="https://github.com/testuser",
        website_url="https://testuser.com",
        bio="Test bio",
    )
    resume.proficiencies.add(proficiency)
    resume.experiences.add(experience, current_experience)
    return resume
