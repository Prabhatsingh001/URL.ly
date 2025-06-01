from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ShortenUrl/", views.make_short_url, name="make_short_url"),
    path("<str:slug>/", views.redirect_url, name="redirect_url"),
    path("delete/<int:id>/", views.delete_url, name="delete_url"),
    path("update_url/<int:id>/", views.update_url, name="update_url"),
]
