"""
Signal handlers for Auth application user management.

This module implements Django signal handlers that automatically:
1. Send welcome emails to newly registered users
2. Create user profiles when new users are registered

All handlers are connected to the post_save signal of the User model
and are automatically registered when the Auth app is loaded.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .tasks import send_welcome_email
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    """
    Send welcome email to newly registered users.

    Args:
        sender: The model class (User)
        instance: The actual User instance that was saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional signal arguments

    This handler is triggered after user creation and sends a welcome
    email with login information and account details.
    """
    if created:
        transaction.on_commit(lambda: send_welcome_email.delay(instance.id))  # type: ignore


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile instance for newly registered users.

    Args:
        sender: The model class (User)
        instance: The actual User instance that was saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional signal arguments

    This handler ensures every new user has an associated profile
    created automatically upon registration.
    """
    if created:
        UserProfile.objects.create(user=instance)
