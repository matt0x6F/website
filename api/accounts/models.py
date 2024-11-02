from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    avatar_link = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
