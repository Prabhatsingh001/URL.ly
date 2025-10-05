"""
URL configuration for UrlShortner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from Auth.views import IndexView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from Biolink.views import (
    Getlinks,
    Addlink,
    my_biolink_page,
    Deletelink,
    editprofile,
    public_biolink_by_slug,
    public_biolink_by_uuid,
    enable_public_link,
)

handler404 = "urlLogic.views.F404_page"
handler500 = "urlLogic.views.F500_page"

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static("logo.png"), permanent=True)),
    path("admin/", admin.site.urls, name="admin"),
    path("auth/", include("social_django.urls", namespace="social")),
    path("", IndexView.as_view(), name="index"),
    path("a/", include(("Auth.urls", "Auth"), namespace="a")),
    path("u/", include(("urlLogic.urls", "urlLogic"), namespace="u")),
    path("my-bio-link-page/", my_biolink_page, name="my_biolink_page"),
    path("biolink-page/<uuid:id>/", Getlinks, name="biolinkpage"),
    path("addlink/<uuid:id>/", Addlink, name="addlink"),
    path("deletelink/<uuid:id>/", Deletelink, name="deletelink"),
    # path for generating a url
    path("editprofile/", editprofile, name="editprofile"),
    path("enable/", enable_public_link, name="enablepubliclink"),
    # path for visiting the public profile
    path("p/<slug:slug>/", public_biolink_by_slug, name="public_biolink_slug"),
    path("u/<uuid:public_id>/", public_biolink_by_uuid, name="public_biolink_uuid"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
