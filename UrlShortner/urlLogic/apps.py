"""
Django application configuration for URL shortening functionality.

This module configures the URL shortening application, which handles:
- URL shortening and management
- URL analytics and tracking
- Signal handlers for URL-related events
"""

from django.apps import AppConfig


class UrllogicConfig(AppConfig):
    """
    Configuration class for the URL shortening application.

    Attributes:
        default_auto_field: Uses BigAutoField for model primary keys
        name: Application identifier in Django project

    The ready() method connects signal handlers for:
    - URL creation events
    - Visit tracking
    - Analytics processing
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "urlLogic"

    def ready(self):
        """
        Initialize application and connect signal handlers.

        Imports the signals module to register URL-related signal handlers
        when the application starts. The noqa comment is used to suppress
        the unused import warning as the import is needed for side effects.
        """
        import urlLogic.signals  # noqa: F401
