"""
Signal handlers for URL model cleanup operations.

This module handles automatic cleanup tasks when URL entries are deleted,
specifically managing associated files like QR codes to prevent orphaned
files in the storage system.
"""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import UrlModel


@receiver(post_delete, sender=UrlModel)
def delete_qr_file(sender, instance, **kwargs):
    """
    Delete associated QR code file when a URL model instance is deleted.

    Args:
        sender: The model class (UrlModel)
        instance: The actual URL instance being deleted
        **kwargs: Additional signal arguments

    This handler ensures that when a URL entry is deleted, its associated
    QR code file is also removed from storage, preventing orphaned files
    and maintaining storage cleanliness.
    """
    if instance.qrcode:
        instance.qrcode.delete(save=False)
