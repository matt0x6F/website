from django.contrib import admin

from blog.models import Comment, File, Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "published")
    list_filter = ("author", "created_at", "published")
    search_fields = ("title", "content", "author__username")
    date_hierarchy = "created_at"


admin.site.register(Post, PostAdmin)


class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("location", "name")


admin.site.register(File, FileAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("content", "author", "post", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("content", "author__username", "post__title")


admin.site.register(Comment, CommentAdmin)
