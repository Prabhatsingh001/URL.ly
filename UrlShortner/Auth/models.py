from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager

# Create your models here.


def validate_file_size(value):
    limit = 2 * 1024 * 1024  # 2 MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2 MiB.")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email, username=username, password=password, **extra_fields
        )


class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )
    email = models.EmailField(_("email address"), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = CustomUserManager()  # type: ignore

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("OTHER", "Other"),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="user_profile_link"
    )
    first_name = models.CharField(max_length=30, editable=True, null=True, blank=True)
    last_name = models.CharField(max_length=20, editable=True, null=True, blank=True)
    phone_number = models.IntegerField(editable=True, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        editable=True,
        validators=[validate_file_size],
    )
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=6, null=True, blank=True, editable=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"this profile belongs to {self.user.email}"


class Contact(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
