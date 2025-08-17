from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .mail import send_welcome_email
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def send_email(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(instance)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
