from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ShortenUrl/", views.make_short_url, name="make_short_url"),
    path("generate_qr/", views.generate_qr, name="generate_qr"),
    path("delete/<int:id>/", views.delete_url, name="delete_url"),
    path("update_url/<int:id>/", views.update_url, name="edit_url"),
    path("<str:slug>/", views.redirect_url, name="redirect_url"),
    path("download-qr/<int:id>/", views.download_qr, name="download_qr"),
]
