from django.contrib import admin

from blog.models import Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "published")
    list_filter = ("author", "created_at", "published")
    search_fields = ("title", "content", "author__username")
    date_hierarchy = "created_at"


admin.site.register(Post, PostAdmin)
