from django.contrib import admin

from blog.models import Comment, File, Post, Series, ShareCode


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "published_at", "created_at", "series")
    list_filter = ("published_at", "author", "series")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at",)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("location", "name")


admin.site.register(File, FileAdmin)
admin.site.register(ShareCode)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "author",
        "created_at",
        "visible",
        "reviewed",
        "parent",
    )
    list_filter = ("visible", "reviewed", "created_at", "author")
    search_fields = ("content", "post__title", "author__username")
    actions = ["mark_visible", "mark_hidden", "mark_reviewed"]

    def mark_visible(self, request, queryset):
        queryset.update(visible=True)

    mark_visible.short_description = "Mark selected comments as visible"

    def mark_hidden(self, request, queryset):
        queryset.update(visible=False)

    mark_hidden.short_description = "Mark selected comments as hidden"

    def mark_reviewed(self, request, queryset):
        queryset.update(reviewed=True)

    mark_reviewed.short_description = "Mark selected comments as reviewed"
