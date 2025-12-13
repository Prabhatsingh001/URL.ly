"""
URL configuration for URL shortening functionality.

This module defines the URL patterns for all URL shortening operations:

Core Features:
- URL shortening and management
- QR code generation and handling
- URL redirection
- URL analytics

URL Patterns:
- /: Dashboard view for URL management
- /shortenurl/: Create new shortened URLs
- /generateqr/: Generate QR codes for URLs
- /delete/<id>/: Delete existing URLs
- /updateurl/<id>/: Update URL settings
- /<slug>/: Redirect to original URL
- /downloadqr/<id>/: Download QR code image
- /mailqr/<id>/: Email QR code to user
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shortenurl/", views.make_short_url, name="make_short_url"),
    path("analytics/<int:id>/", views.analytics_dashboard, name="analytics_dashboard"),
    path("generateqr/", views.generate_qr, name="generate_qr"),
    path("delete/<int:id>/", views.delete_url, name="delete_url"),
    path("updateurl/<int:id>/", views.update_url, name="edit_url"),
    path("<str:slug>/", views.redirect_url, name="redirect_url"),
    path("downloadqr/<int:id>/", views.download_qr, name="download_qr"),
    path("mailqr/<int:id>/", views.mail_qr, name="mail_qr"),
]
