from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from cloudinary_storage.storage import MediaCloudinaryStorage

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
    original_url = models.URLField(
        unique=True, validators=[validate_url_format_and_blacklist]
    )
    short_url = models.CharField(max_length=10, unique=True, null=True, blank=True)
    qrcode = models.ImageField(
        upload_to="qr_code/", null=True, blank=True, storage=MediaCloudinaryStorage()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    device_type = models.CharField(max_length=50, null=True, blank=True)
    screen_resolution = models.CharField(max_length=20, null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    utm_source = models.CharField(max_length=50, null=True, blank=True)
    utm_medium = models.CharField(max_length=50, null=True, blank=True)
    utm_campaign = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    http_method = models.CharField(max_length=10, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]


# ------------------------------------------------------------------------------
