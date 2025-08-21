from django.contrib import admin
from .models import Link, BioLinkProfile
# Register your models here.


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "profile", "created_at")
    list_filter = ("profile",)
    search_fields = ("title", "url")


@admin.register(BioLinkProfile)
class BioLinkProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "user")
    list_display_links = ("id", "display_name")
    search_fields = ("display_name", "user")
