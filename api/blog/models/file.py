from django.db import models


class File(models.Model):
    """
    Tracks https://django-ninja.dev/guides/input/file-params/ which is based on Djangos class by the same name
    """

    posts = models.ManyToManyField("Post", related_name="files")
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
