import re

from ninja import Router
from ninja.errors import HttpError

from auth.middleware import JWTAuth, StaffOnly

from .models import Experience, Proficiency, Resume
from .schemas import ResumeSchema

router = Router()


def validate_url(url: str) -> bool:
    """Validate that a string is a properly formatted URL"""
    if not url:
        return True  # Allow empty URLs
    pattern = r"^https?://.*$"
    return bool(re.match(pattern, url))


def validate_experience_dates(experiences: list) -> None:
    """Validate that experience dates are valid"""
    for exp in experiences:
        if not exp.is_current and exp.end_date and exp.end_date < exp.start_date:
            raise HttpError(400, "End date cannot be before start date")


@router.get("/", response={200: ResumeSchema}, tags=["resume"])
def get_resume(request):
    """Get the resume data"""
    resume = Resume.objects.first()  # We'll only have one resume
    if not resume:
        return {
            "name": "",
            "github_url": "",
            "website_url": "",
            "bio": "",
            "proficiencies": [],
            "experiences": [],
        }

    return {
        "name": resume.name,
        "github_url": resume.github_url,
        "website_url": resume.website_url,
        "bio": resume.bio,
        "proficiencies": [
            {"category": p.category, "items": p.items} for p in resume.proficiencies.all()
        ],
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "is_current": e.is_current,
                "achievements": e.achievements,
            }
            for e in resume.experiences.all()
        ],
    }


@router.put("/", response=ResumeSchema, tags=["resume"], auth=JWTAuth(permissions=StaffOnly))
def update_resume(request, data: ResumeSchema):
    """Update the resume data. Only staff members can update the resume."""
    if not request.user.is_staff:
        raise HttpError(403, "Only staff members can update the resume")

    # Validate URLs
    if not validate_url(data.github_url):
        raise HttpError(400, "Invalid GitHub URL format")
    if not validate_url(data.website_url):
        raise HttpError(400, "Invalid website URL format")

    # Validate experience dates
    validate_experience_dates(data.experiences)

    resume = Resume.objects.first()  # We'll only have one resume
    if not resume:
        resume = Resume()

    # Update basic info
    resume.name = data.name
    resume.github_url = data.github_url
    resume.website_url = data.website_url
    resume.bio = data.bio
    resume.save()

    # Update proficiencies
    resume.proficiencies.all().delete()  # Clear existing proficiencies
    for p in data.proficiencies:
        proficiency = Proficiency.objects.create(category=p.category, items=p.items)
        resume.proficiencies.add(proficiency)

    # Update experiences
    resume.experiences.all().delete()  # Clear existing experiences
    for e in data.experiences:
        experience = Experience.objects.create(
            title=e.title,
            company=e.company,
            start_date=e.start_date,
            end_date=e.end_date,
            is_current=e.is_current,
            achievements=e.achievements,
        )
        resume.experiences.add(experience)

    return {
        "name": resume.name,
        "github_url": resume.github_url,
        "website_url": resume.website_url,
        "bio": resume.bio,
        "proficiencies": [
            {"category": p.category, "items": p.items} for p in resume.proficiencies.all()
        ],
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "is_current": e.is_current,
                "achievements": e.achievements,
            }
            for e in resume.experiences.all()
        ],
    }
