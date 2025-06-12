from datetime import date

import pytest
from django.core.exceptions import ValidationError

from resume.models import Experience, Proficiency, Resume


@pytest.mark.django_db
class TestResumeModels:
    def test_proficiency_creation(self):
        """Test creating a proficiency"""
        proficiency = Proficiency.objects.create(
            category="Programming", items=["Python", "JavaScript"]
        )
        assert proficiency.category == "Programming"
        assert proficiency.items == ["Python", "JavaScript"]
        assert str(proficiency) == "Programming"

    def test_experience_creation(self):
        """Test creating an experience"""
        experience = Experience.objects.create(
            title="Senior Developer",
            company="Test Company",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            is_current=False,
            achievements="- Led team of 5 developers\n- Implemented CI/CD pipeline",
        )
        assert experience.title == "Senior Developer"
        assert experience.company == "Test Company"
        assert experience.start_date == date(2020, 1, 1)
        assert experience.end_date == date(2023, 1, 1)
        assert experience.is_current is False
        assert experience.achievements == "- Led team of 5 developers\n- Implemented CI/CD pipeline"
        assert str(experience) == "Senior Developer at Test Company"

    def test_experience_current_position(self):
        """Test creating a current position experience"""
        experience = Experience.objects.create(
            title="Lead Developer",
            company="Current Company",
            start_date=date(2023, 1, 1),
            is_current=True,
            achievements="Leading team",
        )
        assert experience.is_current is True
        assert experience.end_date is None

    def test_experience_ordering(self):
        """Test experience ordering by start date"""
        exp1 = Experience.objects.create(
            title="Junior Developer",
            company="Company A",
            start_date=date(2020, 1, 1),
            achievements="Junior work",
        )
        exp2 = Experience.objects.create(
            title="Senior Developer",
            company="Company B",
            start_date=date(2022, 1, 1),
            achievements="Senior work",
        )
        exp3 = Experience.objects.create(
            title="Lead Developer",
            company="Company C",
            start_date=date(2023, 1, 1),
            is_current=True,
            achievements="Lead work",
        )

        experiences = Experience.objects.all()
        assert experiences[0] == exp3  # Most recent first
        assert experiences[1] == exp2
        assert experiences[2] == exp1

    def test_resume_creation(self):
        """Test creating a resume with related objects"""
        # Create proficiencies
        prof1 = Proficiency.objects.create(category="Programming", items=["Python", "JavaScript"])
        prof2 = Proficiency.objects.create(category="Frameworks", items=["Django", "React"])

        # Create experiences
        exp1 = Experience.objects.create(
            title="Senior Developer",
            company="Test Company",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            achievements="Test achievements",
        )
        exp2 = Experience.objects.create(
            title="Lead Developer",
            company="Current Company",
            start_date=date(2023, 1, 1),
            is_current=True,
            achievements="Current achievements",
        )

        # Create resume
        resume = Resume.objects.create(
            name="Test User",
            github_url="https://github.com/testuser",
            website_url="https://testuser.com",
            bio="Test bio",
        )

        # Add related objects
        resume.proficiencies.add(prof1, prof2)
        resume.experiences.add(exp1, exp2)

        # Verify relationships
        assert resume.proficiencies.count() == 2
        assert resume.experiences.count() == 2
        assert str(resume) == "Test User's Resume"

    def test_resume_validation(self):
        """Test resume validation"""
        resume = Resume(
            name="Test User",
            github_url="not-a-url",  # Invalid URL
            website_url="https://testuser.com",
            bio="Test bio",
        )
        with pytest.raises(ValidationError):
            resume.full_clean()

    def test_experience_validation(self):
        """Test experience validation"""
        experience = Experience(
            title="Developer",
            company="Test Company",
            start_date=date(2023, 1, 1),
            end_date=date(2020, 1, 1),  # End date before start date
            is_current=False,
            achievements="Test achievements",
        )
        with pytest.raises(ValidationError):
            experience.full_clean()
