from django.db import models


class ShareCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="sharecodes")
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"ShareCode({self.code}) for Post({self.post_id})"
