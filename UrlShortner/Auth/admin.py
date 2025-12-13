"""
Django admin configuration for Auth application models.

This module configures the admin interface for user management, including:
- CustomUser: Extended user model with email authentication
- UserProfile: Additional user profile information
- Contact: Contact form submissions

Each model's admin interface is customized for better usability and security,
with appropriate read-only fields and relevant list displays.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Contact, CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.

    Extends Django's UserAdmin with customizations for email-based authentication:
    - Shows UUID, email, username, and status in list view
    - Organizes fields into logical fieldsets
    - Protects important dates from modification
    """

    model = CustomUser
    list_display = ["id", "email", "username", "is_staff", "is_active"]
    list_display_links = ["id", "email"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Mark it read-only
    readonly_fields = ("last_login", "date_joined")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.

    Displays essential profile information in the admin interface:
    - UUID and full name in list view
    - Phone number for quick reference
    - First name as the clickable link to detail view
    """

    model = UserProfile
    list_display = ["id", "first_name", "last_name", "phone_number"]
    list_display_links = ["id", "first_name"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin configuration for Contact model.

    Provides a simple interface for reviewing contact form submissions:
    - Shows UUID and contact information in list view
    - Name field links to full message details
    - Maintains chronological record of all submissions
    """

    model = Contact
    list_display = ["id", "name", "email"]
    list_display_links = ["id", "name"]
