from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, unique_for_date="published_at", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    series = models.ForeignKey(
        "Series", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Ensure slug is unique for the publication date if published_at is set
        # This logic might be more complex depending on how you handle drafts vs published slugs
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.published_at:
            return reverse(
                "blog-post",  # Make sure this route name matches your UI expectations or a DRF route
                kwargs={
                    "year": self.published_at.year,
                    # "month": self.published_at.strftime("%m"), # if you use month in URL
                    # "day": self.published_at.strftime("%d"),   # if you use day in URL
                    "slug": self.slug,
                },
            )
        return reverse(
            "admin-posts-edit", kwargs={"id": self.id}
        )  # Fallback for drafts or non-public posts


class Series(models.Model):
    title = models.CharField(max_length=255, unique=True, default="")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Series"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.title:
            # This case should ideally be prevented by form/API validation
            # but as a fallback for the default="", ensure a unique title if possible
            # or raise an error. For now, we rely on unique=True to catch issues.
            pass
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse('series_detail', kwargs={'slug': self.slug}) # If you have a public series detail page


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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    visible = models.BooleanField(default=True)
    reviewed = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)  # Internal notes for moderation

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
