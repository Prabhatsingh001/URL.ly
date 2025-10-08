from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shortenurl/", views.make_short_url, name="make_short_url"),
    path("generateqr/", views.generate_qr, name="generate_qr"),
    path("delete/<int:id>/", views.delete_url, name="delete_url"),
    path("updateurl/<int:id>/", views.update_url, name="edit_url"),
    path("<str:slug>/", views.redirect_url, name="redirect_url"),
    path("downloadqr/<int:id>/", views.download_qr, name="download_qr"),
    path("mailqr/<int:id>/", views.mail_qr, name="mail_qr"),
]
