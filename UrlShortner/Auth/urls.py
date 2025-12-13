"""
URL configuration for the Auth module.

This module defines the URL patterns for authentication and user management features including:
- User registration and email verification
- Login and logout functionality
- Profile management (view, edit, password update)
- Password reset workflow
- About and contact pages

Each URL pattern is mapped to its corresponding view function or class in the views module.
"""

from django.urls import path

from . import views
from .views import AboutView

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", views.contact, name="contact"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/<uuid:id>/", views.profile, name="profile"),
    path("profile-edit/<uuid:id>/", views.update_profile, name="edit_profile"),
    path("profile-password/<uuid:id>/", views.update_password, name="update_password"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "resend-verification/<str:email>/",
        views.resend_verification_email,
        name="resend-verification-email",
    ),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path(
        "reset_password/<uidb64>/<token>/", views.reset_password, name="reset_password"
    ),
]
