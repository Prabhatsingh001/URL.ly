from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile
from .mail import send_verification_mail, send_welcome_email


@receiver(post_save, sender=CustomUser)
def send_email(sender, instance, created, **kwargs):
    if created:
        # welcome email
        send_welcome_email(instance)
        # account activation email
        send_verification_mail(instance)


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
