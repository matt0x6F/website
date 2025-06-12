import re

from django.core.exceptions import ValidationError
from django.db import models


def validate_url(value):
    """Validate that a string is a properly formatted URL"""
    if not value:
        return
    pattern = r"^https?://.*$"
    if not re.match(pattern, value):
        raise ValidationError("Invalid URL format")


# Create your models here.


class Proficiency(models.Model):
    category = models.CharField(max_length=100)
    items = models.JSONField()  # List of proficiency items

    class Meta:
        verbose_name_plural = "Proficiencies"

    def __str__(self):
        return self.category


class Experience(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    achievements = models.TextField()  # Markdown formatted achievements

    class Meta:
        verbose_name_plural = "Experience"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} at {self.company}"

    def clean(self):
        if not self.is_current and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")


class Resume(models.Model):
    name = models.CharField(max_length=200)
    github_url = models.URLField(validators=[validate_url])
    website_url = models.URLField(validators=[validate_url])
    bio = models.TextField()
    proficiencies = models.ManyToManyField(Proficiency)
    experiences = models.ManyToManyField(Experience)

    def __str__(self):
        return f"{self.name}'s Resume"
