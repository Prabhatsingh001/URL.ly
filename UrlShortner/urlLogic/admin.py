"""
Django admin configuration for URL shortening functionality.

This module configures the admin interface for managing:
- URL mappings (both authenticated and anonymous)
- URL visit analytics
- Administrative controls for shortened URLs

Provides a customized admin interface with search, filtering,
and display options for effective URL management.
"""

from django.contrib import admin

from .models import ShortUrlAnonymous, UrlModel, UrlVisit

admin.site.site_header = "URL Shortener Admin"


class UrlModelAdmin(admin.ModelAdmin):
    """
    Admin interface customization for URL management.

    Features:
    - Comprehensive list view with URL details and analytics
    - Click-through access to detailed URL information
    - Search functionality for URLs
    - Filtering by creation and expiration dates
    - Chronological ordering with newest first

    The interface provides all necessary tools for URL monitoring
    and management by administrative users.
    """

    list_display = (
        "original_url",
        "short_url",
        "created_at",
        "expires_at",
        "click_count",
        "user",
    )
    list_display_links = ("user", "short_url", "original_url")
    search_fields = ("original_url", "short_url")
    list_filter = ("created_at", "expires_at")
    ordering = ("-created_at",)


# Register models with admin site
# UrlModel with custom admin configuration for enhanced management
admin.site.register(UrlModel, UrlModelAdmin)

# UrlVisit for tracking URL access analytics
admin.site.register(UrlVisit)

# ShortUrlAnonymous for managing anonymous user URL shortening
admin.site.register(ShortUrlAnonymous)
