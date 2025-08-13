from django.db import models
import uuid
from django.conf import settings
from django.utils.text import slugify

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # Public slug: unique link like /p/yourname
    public_slug = models.SlugField(max_length=50, unique=True, blank=True)
    # Fallback public UUID (optional, for /u/<uuid>)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.public_slug:
            base = self.user.username or f"user-{self.user.pk}"
            candidate = slugify(base)[:40] or str(self.public_id)[:12]
            # ensure uniqueness
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
