"""
Django settings for URL.ly project.

This module manages all Django settings for both development and production environments.
Configuration is handled through environment variables using python-decouple.

Key Features:
- Environment-specific settings (DEBUG vs Production)
- Security settings (SECRET_KEY, ALLOWED_HOSTS, etc.)
- Database configuration (SQLite for dev, PostgreSQL for prod)
- Authentication backends (Django + Google OAuth2)
- Email configuration
- Celery task queue settings
- Static/Media file handling with Cloudinary
- Custom user model integration
- Social authentication pipeline
- TailwindCSS configuration

Environment Variables:
    Required:
    - SECRET_KEY: Django secret key
    - GOOGLE_CLIENT_ID: Google OAuth client ID
    - GOOGLE_CLIENT_SECRET: Google OAuth client secret
    - EMAIL_* settings for email configuration
    - CLOUDINARY_* settings for media storage
    - DATABASE_* settings for production database

    Optional:
    - DEBUG: Set to True for development environment (default: False)
    - CELERY_BROKER_URL: Redis URL for production (uses localhost in dev)

Security:
    Production environment enables additional security features:
    - Secure cookies
    - HTTPS-only
    - WhiteNoise for static files
    - PostgreSQL with SSL
"""

import os
from pathlib import Path

from decouple import config

DEBUG = config("DEBUG", cast=bool, default=False)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("GOOGLE_CLIENT_SECRET")

EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
SUPPORT_EMAIL = config("SUPPORT_EMAIL")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

if DEBUG:
    CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
else:
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", cast=str)

CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")

SALT = config("SALT", cast=str)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

LOGIN_URL = "/a/login/"
LOGIN_REDIRECT_URL = "/u/"
LOGOUT_REDIRECT_URL = "/"

if DEBUG:
    SOCIAL_AUTH_RAISE_EXCEPTIONS = True
    SITE_DOMAIN = "127.0.0.1:8000"
    PROTOCOL = "http"
    TAILWIND_APP_NAME = "theme"
    NPM_BIN_PATH = "C:\\Program Files\\nodejs\\npm.cmd"
    ALLOWED_HOSTS = ["127.0.0.1"]
else:
    SITE_DOMAIN = "url-ly.onrender.com"
    PROTOCOL = "https"
    ALLOWED_HOSTS = [".onrender.com"]


APPEND_SLASH = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary",
    "django.contrib.staticfiles",
    "social_django",
    "Auth",
    "urlLogic",
    "Biolink",
    "Brandlink",
    "blog",
    "tailwind",
    "theme",
]

if DEBUG:
    INSTALLED_APPS += [
        "django_browser_reload",
        "django_extensions",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "UrlShortner.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
            ],
        },
    },
]

WSGI_APPLICATION = "UrlShortner.wsgi.application"

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT", cast=int),
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "Auth.CustomUser"

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_build", "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CONN_MAX_AGE = 60
    CSRF_TRUSTED_ORIGINS = ["https://url-ly.onrender.com"]

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "Auth.pipelines.save_profile",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "Auth.pipelines.activate_google_user",
)
