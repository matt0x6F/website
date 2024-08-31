from django.db import models


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True, default=None)
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title
