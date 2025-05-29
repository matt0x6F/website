from django.db import models
from django.utils.text import slugify


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
