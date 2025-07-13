from .models import UrlModel
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=UrlModel)
def delete_qr_file(sender, instance, **kwargs):
    if instance.qrcode:
        instance.qrcode.delete(save=False)
