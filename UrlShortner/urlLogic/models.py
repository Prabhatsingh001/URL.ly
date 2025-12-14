from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from cloudinary_storage.storage import MediaCloudinaryStorage
# from Brandlink.models import Domain

User = get_user_model()


# ------------------------------------------------------------------------------
class ShortUrlAnonymous(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=6, unique=True, blank=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"


# ------------------------------------------------------------------------------
"""all the logic for logged in users"""

BLACKLISTED_DOMAINS = [
    "url-ly.onrender.com",
    "localhost",
    "127.0.0.1",
]


def validate_url_format_and_blacklist(value):
    parsed_url = urlparse(value)
    print(parsed_url)

    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValidationError("Invalid URL format.")

    domain = parsed_url.netloc.lower()

    for blocked in BLACKLISTED_DOMAINS:
        if blocked in domain:
            raise ValidationError("This domain is not allowed.")


class UrlModel(models.Model):
    # domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, blank=True)
    original_url = models.URLField(
        unique=True, validators=[validate_url_format_and_blacklist]
    )
    short_url = models.CharField(max_length=10, unique=True, null=True, blank=True)
    qrcode = models.ImageField(
        upload_to="qr_code/", null=True, blank=True, storage=MediaCloudinaryStorage()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, default=None)
    click_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    #     unique_together = ("domain", "short_url")

    def __str__(self):
        return f"{self.short_url}"


class UrlVisit(models.Model):
    url = models.ForeignKey("UrlModel", on_delete=models.CASCADE, related_name="visits")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    browser = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    device = models.CharField(max_length=50, null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.url} -> {self.url.click_count} -> {self.url.original_url}"  # type: ignore


# ------------------------------------------------------------------------------
