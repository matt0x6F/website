from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar_link = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.URLField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Username still required by AbstractUser

    @property
    def name(self):
        """Return the full name or username if no name is set"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    @property
    def avatar(self):
        """Return the avatar link if set"""
        return self.avatar_link

    @property
    def url(self):
        """Return the website URL if set"""
        return self.website_url
