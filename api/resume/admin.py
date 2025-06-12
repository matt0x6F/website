from django.contrib import admin

from .models import Experience, Proficiency, Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("name", "github_url", "website_url")
    filter_horizontal = ("proficiencies", "experiences")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "company")
    search_fields = ("title", "company", "achievements")


@admin.register(Proficiency)
class ProficiencyAdmin(admin.ModelAdmin):
    list_display = ("category",)
    search_fields = ("category", "items")
