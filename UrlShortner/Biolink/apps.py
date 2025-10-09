"""
Django application configuration for the Biolink feature.

This module configures the Bio Link application, which provides:
- User profile pages with customizable links
- Automatic profile creation
- Signal handlers for profile management
- Database configuration
"""

from django.apps import AppConfig


class BiolinkConfig(AppConfig):
    """
    Configuration class for the Biolink application.

    Attributes:
        default_auto_field: Uses BigAutoField for model primary keys
        name: Application identifier in Django project

    The ready() method connects signal handlers for:
    - Automatic profile creation
    - Profile synchronization
    - Image processing events
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "Biolink"

    def ready(self):
        """
        Initialize application and connect signal handlers.

        Imports the signals module to register profile-related handlers
        when the application starts. The noqa comment suppresses the
        unused import warning as the import is needed for side effects.
        """
        import Biolink.signals  # noqa: F401
