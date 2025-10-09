"""
Signal handlers for automatic Biolink profile management.

This module handles the automatic creation of Biolink profiles
when new users are registered in the system. It ensures that
every user has an associated profile for managing their bio links.

The signals are connected automatically when the Biolink app is loaded
through the apps.py configuration.
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BioLinkProfile

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a Biolink profile when a new user is registered.

    Args:
        sender: The model class (User)
        instance: The actual User instance that was saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional signal arguments

    This handler ensures every new user automatically gets a Biolink
    profile created. The profile uses default values and can be
    customized later by the user.

    Note: Only triggers on user creation, not on updates.
    """
    if created:
        BioLinkProfile.objects.create(user=instance)
