"""
Django admin configuration for Biolink feature management.

This module configures the admin interface for managing:
- User bio link profiles
- Individual links within profiles
- Profile and link relationships

Provides administrative tools for content moderation and user management
with filtering, search, and display customization.
"""

from django.contrib import admin

from .models import BioLinkProfile, Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Link model.

    Features:
    - List view with title, URL, profile association, and creation date
    - Filtering by profile to manage links per user
    - Search functionality for link titles and URLs
    - Chronological tracking of link creation

    This interface allows administrators to monitor and manage
    all links across different user profiles efficiently.
    """

    list_display = ("title", "url", "profile", "created_at")
    list_filter = ("profile",)
    search_fields = ("title", "url")


@admin.register(BioLinkProfile)
class BioLinkProfileAdmin(admin.ModelAdmin):
    """
    Admin interface customization for BioLinkProfile model.

    Features:
    - List view with profile ID, display name, and user association
    - Clickable links for quick profile access
    - Search functionality for display names and users
    - Efficient profile management and monitoring

    Provides administrators with tools to manage user profiles
    and maintain oversight of profile content and relationships.
    """

    list_display = ("id", "display_name", "user")
    list_display_links = ("id", "display_name")
    search_fields = ("display_name", "user")
