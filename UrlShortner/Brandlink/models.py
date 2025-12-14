# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Domain(models.Model):
#     domain = models.CharField(max_length=255, unique=True)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     is_verified = models.BooleanField(default=False)
#     verification_code = models.CharField(max_length=64)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
