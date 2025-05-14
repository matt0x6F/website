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
    series = models.ForeignKey(
        "Series", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.title


class Series(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "series"


class File(models.Model):
    """
    Tracks https://django-ninja.dev/guides/input/file-params/ which is based on Djangos class by the same name
    """

    posts = models.ManyToManyField(Post, related_name="files")
    name = models.CharField(max_length=255)
    content_type = models.CharField()
    charset = models.CharField(blank=True, null=True)
    visibility = models.CharField(
        choices=[("public", "public"), ("private", "private")], default="public"
    )
    size = models.IntegerField()  # bytes
    location = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="children",
    )
    visible = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return self.content
