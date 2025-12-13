"""
Root URL configuration for URL.ly project.

This module defines the main URL routing for the entire application, integrating
all sub-applications and their URL patterns. The routing structure is organized as follows:

Main Routes:
- / : Main landing page (IndexView)
- /s/ : URL shortening functionality
- /a/ : Authentication and user management
- /u/ : User dashboard and URL management
- /p/ : Public biolink pages
- /admin/ : Admin interface

Features:
- URL shortening with anonymous access
- Social authentication integration
- Biolink page management
- Custom error handlers (404, 500, 403)
- Static file serving in development
- Browser reload support in debug mode

Note: Static file serving is only enabled in DEBUG mode. In production,
static files should be served by the web server or a CDN.
"""

from Auth.views import IndexView
from Biolink.views import (
    Addlink,
    Deletelink,
    Getlinks,
    editprofile,
    enable_public_link,
    my_biolink_page,
    public_biolink_by_slug,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from urlLogic.views import (
    anonymousShorturl,
    get_original_url,
    redirect_to_original,
)

handler404 = "urlLogic.errors.F404_page"
handler500 = "urlLogic.errors.F500_page"
handler403 = "urlLogic.errors.custom_403_view"


urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path("admin/", admin.site.urls, name="admin"),
    path("auth/", include("social_django.urls", namespace="social")),
    path("", IndexView.as_view(), name="index"),
    path("preview/", get_original_url, name="preview"),
    path("s/", anonymousShorturl, name="urlshort"),
    path("s/<str:short_code>/", redirect_to_original, name="redirect"),
    path("a/", include(("Auth.urls", "Auth"), namespace="a")),
    path("u/", include(("urlLogic.urls", "urlLogic"), namespace="u")),
    path("my-bio-link-page/", my_biolink_page, name="my_biolink_page"),
    path("biolink-page/<uuid:id>/", Getlinks, name="biolinkpage"),
    path("addlink/<uuid:id>/", Addlink, name="addlink"),
    path("deletelink/<uuid:id>/", Deletelink, name="deletelink"),
    path("editprofile/<uuid:id>/", editprofile, name="editprofile"),
    path("enable/", enable_public_link, name="enablepubliclink"),
    path("p/<slug:slug>/", public_biolink_by_slug, name="public_biolink_slug"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
