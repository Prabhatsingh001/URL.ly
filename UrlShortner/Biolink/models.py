"""
Database models for the Biolink feature, providing user profile pages with multiple links.

This module defines the data structure for:
- User bio link profiles with customizable information
- Individual links within profiles
- Image handling with automatic optimization

Key features:
- UUID-based primary keys for security
- Automatic image processing and optimization
- Cloud storage integration for media
- Customizable profile slugs for public URLs
"""

import uuid
from io import BytesIO

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image

User = settings.AUTH_USER_MODEL


class BioLinkProfile(models.Model):
    """
    User profile model for bio link pages.

    This model represents a user's customizable profile page that can contain
    multiple links and personal information. It includes automatic image
    processing for profile pictures.

    Attributes:
        id (UUIDField): Unique identifier for the profile
        user (OneToOneField): Associated user account
        display_name (CharField): Public display name
        bio (CharField): Short biography or description
        profile_image (ImageField): Profile picture with auto-optimization
        public_slug (SlugField): Custom URL for public profile

    The save method includes automatic image processing:
    - Converts RGBA/P images to RGB
    - Resizes images to max 500x500
    - Optimizes JPEG quality to 85%
    - Handles cloud storage upload
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="biolinkprofile"
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])
        ],
        storage=MediaCloudinaryStorage(),
    )
    public_slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override save method to process profile images before saving.

        Process includes:
        - Converting image mode to RGB if needed
        - Resizing to maximum 500x500 pixels
        - Optimizing JPEG quality
        - Handling cloud storage upload

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        if self.profile_image:
            img = Image.open(self.profile_image)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            self.profile_image.save(
                self.profile_image.name, ContentFile(buffer.read()), save=False
            )

        super().save(*args, **kwargs)


class Link(models.Model):
    """
    Individual link model for items within a bio link profile.

    This model represents a single link entry in a user's profile page.
    Links can be made public or private and are ordered by creation date.

    Attributes:
        id (UUIDField): Unique identifier for the link
        profile (ForeignKey): Associated BioLinkProfile
        title (CharField): Display text for the link
        url (URLField): Destination URL
        is_public (BooleanField): Visibility toggle
        created_at (DateTimeField): Timestamp of creation

    Meta:
        ordering: Links are ordered by creation date (newest first)
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    profile = models.ForeignKey(
        BioLinkProfile,
        on_delete=models.CASCADE,
        related_name="links",
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        String representation of the Link model.

        Returns:
            str: Formatted string showing link title and associated username
        """
        return f"{self.title} --> {self.profile.user.username}"
