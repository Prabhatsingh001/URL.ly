from django.db import models
import uuid
from django.conf import settings

from django.core.validators import FileExtensionValidator
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

User = settings.AUTH_USER_MODEL


class BioLinkProfile(models.Model):
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
        return f"{self.title} --> {self.profile.user.username}"
