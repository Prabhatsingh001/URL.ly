from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BioLinkProfile
from django.conf import settings

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        BioLinkProfile.objects.create(user=instance)
