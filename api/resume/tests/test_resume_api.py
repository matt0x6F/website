import pytest
from django.test.client import Client

from accounts.models import User


@pytest.mark.django_db
class TestResumeAPI:
    @pytest.fixture
    def staff_user(self, db):
        return User.objects.create_user(
            username="staff", email="staff@example.com", password="staffpass", is_staff=True
        )

    @pytest.fixture
    def regular_user(self, db):
        return User.objects.create_user(
            username="user", email="user@example.com", password="userpass", is_staff=False
        )

    @pytest.fixture
    def staff_token(self, staff_user):
        from ninja_jwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(staff_user)
        return str(refresh.access_token)

    @pytest.fixture
    def regular_token(self, regular_user):
        from ninja_jwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(regular_user)
        return str(refresh.access_token)

    @pytest.fixture
    def resume_data(self):
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

    def test_get_resume_empty(self, client: Client):
        """Test getting resume when none exists"""
        response = client.get("/api/resume/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == ""
        assert data["github_url"] == ""
        assert data["website_url"] == ""
        assert data["bio"] == ""
        assert data["proficiencies"] == []
        assert data["experiences"] == []

    def test_get_resume_with_data(self, client: Client, resume, resume_data):
        """Test getting resume with existing data"""
        response = client.get("/api/resume/")
        assert response.status_code == 200
        data = response.json()

        # Verify basic info
        assert data["name"] == resume_data["name"]
        assert data["github_url"] == resume_data["github_url"]
        assert data["website_url"] == resume_data["website_url"]
        assert data["bio"] == resume_data["bio"]

        # Verify proficiencies
        assert len(data["proficiencies"]) == len(resume_data["proficiencies"])
        for prof in data["proficiencies"]:
            matching_prof = next(
                p for p in resume_data["proficiencies"] if p["category"] == prof["category"]
            )
            assert prof["items"] == matching_prof["items"]

        # Verify experiences
        assert len(data["experiences"]) == len(resume_data["experiences"])
        for exp in data["experiences"]:
            matching_exp = next(e for e in resume_data["experiences"] if e["title"] == exp["title"])
            assert exp["company"] == matching_exp["company"]
            assert exp["start_date"] == matching_exp["start_date"]
            assert exp["is_current"] == matching_exp["is_current"]
            assert exp["achievements"] == matching_exp["achievements"]
            if "end_date" in matching_exp:
                assert exp["end_date"] == matching_exp["end_date"]

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_resume_staff(self, client: Client, auth_token: str, resume_data):
        """Test updating resume data as staff"""
        # First create initial resume
        initial_data = {
            "name": "Initial Name",
            "github_url": "https://github.com/initial",
            "website_url": "https://initial.com",
            "bio": "Initial bio",
            "proficiencies": [],
            "experiences": [],
        }

        response = client.put(
            "/api/resume/",
            initial_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200

        # Then update with new data
        response = client.put(
            "/api/resume/",
            resume_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 200
        data = response.json()

        # Verify updated data
        assert data["name"] == resume_data["name"]
        assert data["github_url"] == resume_data["github_url"]
        assert data["website_url"] == resume_data["website_url"]
        assert data["bio"] == resume_data["bio"]
        assert len(data["proficiencies"]) == len(resume_data["proficiencies"])
        assert len(data["experiences"]) == len(resume_data["experiences"])

    @pytest.mark.parametrize("auth_token", ["regular_user"], indirect=True)
    def test_update_resume_non_staff_forbidden(self, client: Client, auth_token: str, resume_data):
        """Test that non-staff users cannot update resume"""
        response = client.put(
            "/api/resume/",
            resume_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 403

    def test_update_resume_unauthenticated_forbidden(self, client: Client, resume_data):
        """Test that unauthenticated users cannot update resume"""
        response = client.put("/api/resume/", resume_data, content_type="application/json")
        assert response.status_code == 403

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_resume_validation(self, client: Client, auth_token: str):
        """Test resume update validation"""
        invalid_data = {
            "name": "Test User",
            "github_url": "not-a-url",  # Invalid URL
            "website_url": "https://testuser.com",
            "bio": "Test bio",
            "proficiencies": [],
            "experiences": [],
        }

        response = client.put(
            "/api/resume/",
            invalid_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("auth_token", ["superuser"], indirect=True)
    def test_update_resume_experience_validation(self, client: Client, auth_token: str):
        """Test resume experience validation"""
        invalid_data = {
            "name": "Test User",
            "github_url": "https://github.com/testuser",
            "website_url": "https://testuser.com",
            "bio": "Test bio",
            "proficiencies": [],
            "experiences": [
                {
                    "title": "Developer",
                    "company": "Test Company",
                    "start_date": "2023-01-01",
                    "end_date": "2020-01-01",  # End date before start date
                    "is_current": False,
                    "achievements": "Test achievements",
                }
            ],
        }

        response = client.put(
            "/api/resume/",
            invalid_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        )
        assert response.status_code == 400
