from django.contrib import admin
from .models import UrlModel

# Register your models here.
admin.site.site_header = "URL Shortener Admin"


class UrlModelAdmin(admin.ModelAdmin):
    list_display = (
        "original_url",
        "short_url",
        "created_at",
        "expires_at",
        "click_count",
        "user",
    )
    search_fields = ("original_url", "short_url")
    list_filter = ("created_at", "expires_at")
    ordering = ("-created_at",)


admin.site.register(UrlModel, UrlModelAdmin)
