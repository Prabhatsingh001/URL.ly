"""
Database models for the authentication and user management system.

This module defines the core data models for user authentication and profile management:
- CustomUser: Extended Django user model with email authentication
- UserProfile: Additional user information and preferences
- Contact: Contact form submission storage

The models use UUID as primary keys for better security and scalability.
"""

import uuid

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


def validate_file_size(value):
    """
    Validate that uploaded files don't exceed the size limit.

    Args:
        value: The uploaded file object to validate

    Raises:
        ValidationError: If file size exceeds 2 MiB

    This validator is used primarily for profile image uploads.
    """
    limit = 2 * 1024 * 1024  # 2 MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2 MiB.")


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager with email as the unique identifier.

    This manager handles user creation and superuser creation with email-based authentication
    instead of Django's default username-based authentication.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, username, and password.

        Args:
            email: User's email address (required)
            username: User's username (required)
            password: User's password (optional)
            **extra_fields: Additional fields to be saved on the user model

        Returns:
            The created user instance

        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, username, and password.

        Args:
            email: Superuser's email address (required)
            username: Superuser's username (required)
            password: Superuser's password (optional)
            **extra_fields: Additional fields to be saved on the user model

        Returns:
            The created superuser instance

        Raises:
            ValueError: If is_staff or is_superuser is not True
        """
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
    """
    Custom user model that extends Django's AbstractUser.

    This model uses email as the primary identifier for authentication instead of username.
    It also includes additional fields for tracking user creation and updates.

    Attributes:
        id: UUID primary key
        email: Unique email address for authentication
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
        is_active: Whether the user's email is verified
        is_staff: Whether the user has admin access
    """

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )
    email = models.EmailField(_("email address"), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = CustomUserManager()  # type: ignore

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Extended profile information for CustomUser.

    This model stores additional user information that isn't part of the core
    authentication system. It has a one-to-one relationship with CustomUser.

    Attributes:
        id: UUID primary key
        user: One-to-one relationship with CustomUser
        first_name: User's first name
        last_name: User's last name
        phone_number: User's phone number (optional)
        profile_image: User's profile picture (optional, max 2MB)
        gender: User's gender selection (optional)
        created_at: Timestamp of profile creation
        updated_at: Timestamp of last update
    """

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
    phone_number = PhoneNumberField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        editable=True,
        validators=[validate_file_size],
        storage=MediaCloudinaryStorage(),
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

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Contact(models.Model):
    """
    Contact form submission model.

    Stores messages submitted through the contact form for admin review.
    Each submission includes the sender's information and their message.

    Attributes:
        id: UUID primary key
        name: Sender's name
        email: Sender's email address
        message: The content of the contact message
        created_at: Timestamp of message submission
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
