from django.urls import path
from . import views
from .views import AboutView

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", views.contact, name="contact"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path(
        "reset_password/<uidb64>/<token>/", views.reset_password, name="reset_password"
    ),
]
