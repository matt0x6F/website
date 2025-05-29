from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


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
