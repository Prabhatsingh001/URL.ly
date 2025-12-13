"""
Django application configuration for the Auth app.

This module configures the Auth application, which handles:
- User authentication and authorization
- User profile management
- Social authentication integration
- Contact form processing
"""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """
    Configuration class for the Auth application.

    Attributes:
        default_auto_field: Specifies BigAutoField as the primary key type
        name: Application label used in project configuration

    The ready() method connects signal handlers for:
    - User profile creation on user registration
    - Email notifications
    - Social auth processing
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "Auth"

    def ready(self):
        import Auth.signals  # noqa: F401
