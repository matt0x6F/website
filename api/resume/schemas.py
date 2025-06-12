from datetime import date
from typing import List, Optional

from ninja import Schema


class ProficiencySchema(Schema):
    category: str
    items: List[str]


class ExperienceSchema(Schema):
    title: str
    company: str
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    achievements: str  # Markdown formatted achievements


class ResumeSchema(Schema):
    name: str
    github_url: str  # We'll validate URLs in the API layer
    website_url: str  # We'll validate URLs in the API layer
    bio: str
    proficiencies: List[ProficiencySchema]
    experiences: List[ExperienceSchema]
