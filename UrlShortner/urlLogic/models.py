from django.db import models
from django.contrib.auth import get_user_model
import uuid
# Create your models here.

User = get_user_model()


class UrlModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_url = models.URLField(unique=True)
    short_url = models.CharField(max_length=10, unique=True, null=True, blank=True)
    qrcode = models.ImageField(upload_to="qr_code/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.short_url}"
