from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    # Public pages
    path("", views.blog_list, name="blog_list"),
    path("author/<str:username>/", views.author_profile, name="author_profile"),
    path("post/<slug:slug>/", views.view_blog_post, name="blog_post_detail"),
    # Dashboard (authenticated)
    path("dashboard/", views.blog_home, name="blog_home"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("create/", views.create_blog_post, name="create_blog_post"),
    path("edit/<slug:slug>/", views.edit_blog_post, name="edit_blog_post"),
    path("delete/<slug:slug>/", views.delete_blog_post, name="delete_blog_post"),
    path(
        "post/<slug:slug>/status/", views.update_blog_status, name="update_blog_status"
    ),
    # Interactions
    path("posts/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"
    ),
]
