from django.urls import path

from . import views

urlpatterns = [
    path("", views.blog_home, name="blog_home"),
    path("create/", views.create_blog_post, name="create_blog_post"),
]
