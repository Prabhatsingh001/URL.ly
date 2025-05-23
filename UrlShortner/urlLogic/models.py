from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()


class UrlModel(models.Model):
    original_url = models.URLField()
    short_url = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
