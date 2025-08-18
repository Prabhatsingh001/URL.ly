from django.db import models
import uuid
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from cloudinary_storage.storage import MediaCloudinaryStorage

User = settings.AUTH_USER_MODEL
# Create your models here.


class Link(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} --> {self.user.username}"


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
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        base_source = (
            self.display_name.strip()
            if self.display_name
            else (self.user.username or f"user-{self.user.pk}")
        )
        candidate = slugify(base_source)[:40] or str(self.public_id)[:12]

        # If slug is missing or doesn't match the expected base, regenerate it
        if not self.public_slug or not self.public_slug.startswith(
            slugify(base_source)[:40]
        ):
            unique = candidate
            i = 1
            while (
                BioLinkProfile.objects.filter(public_slug=unique)
                .exclude(pk=self.pk)
                .exists()
            ):
                unique = f"{candidate}-{i}"
                i += 1
            self.public_slug = unique

        super().save(*args, **kwargs)
