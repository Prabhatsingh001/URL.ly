"""
Social authentication pipeline functions for python-social-auth integration.

This module provides custom pipeline functions for handling social authentication
workflows, specifically for:
- Creating/updating user profiles from social auth data
- Automatically activating users who authenticate via Google OAuth2

These functions are designed to be included in the SOCIAL_AUTH_PIPELINE setting.
"""

from django.contrib.auth import get_user_model

from .models import UserProfile as Profile

User = get_user_model()


def save_profile(strategy, details, response, user=None, *args, **kwargs):
    """
    Pipeline function to create or update user profile from social auth data.

    Args:
        strategy: The social auth strategy in use
        details: Dictionary with user details from the provider
        response: Dictionary with the raw response from the provider
        user: The user instance being processed
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments

    Creates a UserProfile if it doesn't exist, and updates the first_name
    and last_name fields using the fullname provided by the social auth provider.
    """
    if user is None:
        return

    profile, created = Profile.objects.get_or_create(user=user)
    if created or not profile.first_name:
        profile.first_name = details.get("fullname").split(" ")[0]

    if created or not profile.last_name:
        profile.last_name = details.get("fullname").split(" ")[1]

    profile.save()


def activate_google_user(strategy, backend, user=None, *args, **kwargs):
    """
    Pipeline function to automatically activate users who sign in with Google.

    Args:
        strategy: The social auth strategy in use
        backend: The authentication backend being used
        user: The user instance being processed
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments

    Automatically sets is_active=True for users authenticating via Google OAuth2,
    bypassing the email verification requirement for these users since Google
    accounts already have verified email addresses.
    """
    if backend.name == "google-oauth2" and user:
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        return
