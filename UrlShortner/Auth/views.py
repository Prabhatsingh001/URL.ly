from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token, password_reset_token
from django.core.mail import EmailMessage
from .models import Contact, UserProfile
from .mail import send_contact_email

from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# import json
# import os
# from datetime import datetime


# Create your views here.
CusUser = get_user_model()


# def debug_request(request):
#     data = {
#         "method": request.method,
#         "path": request.path,
#         "full_path": request.get_full_path(),
#         "scheme": request.scheme,
#         "encoding": request.encoding,
#         "content_type": request.content_type,
#         "user_agent": request.META.get("HTTP_USER_AGENT"),
#         "client_ip": request.META.get("REMOTE_ADDR"),
#         "query_params": dict(request.GET),
#         "post_data": dict(request.POST),
#         "cookies": request.COOKIES,
#         "session": dict(request.session.items()) if hasattr(request, "session") else {},
#         "meta": {
#             k: str(v) for k, v in request.META.items()
#         },  # serialize all META safely
#         "timestamp": datetime.now().isoformat(),
#     }

#     # File path (logs/debug_requests.json)
#     log_dir = os.path.join(os.getcwd(), "logs")
#     os.makedirs(log_dir, exist_ok=True)
#     file_path = os.path.join(log_dir, "debug_requests.json")

#     # Append to file
#     with open(file_path, "a", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)
#         f.write("\n\n")  # separate requests


class IndexView(View):
    def get(self, request):
        # debug_request(request)
        if request.user.is_authenticated:
            return redirect("u:home")
        return render(request, "index.html")


class AboutView(TemplateView):
    template_name = "about.html"


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            contact = Contact.objects.create(name=name, email=email, message=message)
            send_contact_email(contact)
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("a:contact")
        else:
            messages.error(request, "All fields are required.")
    return render(request, "contact.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("confirm-password")

        if CusUser.objects.filter(email=email).exists():
            messages.error(request, "email already exists")
            return redirect("a:signup")

        # if CusUser.objects.filter(username=username).exists():
        #     messages.error(request, "username already exists")
        #     return redirect("a:signup")

        if password != password2:
            messages.error(request, "passwords do not match")
            return redirect("a:signup")

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("a:signup")

        # if len(username) < 4:
        #     messages.error(request, "username must be at least 4 characters")
        #     return redirect("a:signup")

        # if len(username) > 20:
        #     messages.error(request, "username must be at most 20 characters")
        #     return redirect("a:signup")

        user = CusUser.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.set_password(password)  # Hash the password
        user.is_active = False
        user.save()
        messages.success(
            request, "User created successfully, please verify your email before login"
        )
        """
        email sending functionality handled by signals now
        """
        return redirect("a:login")
    return render(request, "signup.html")


def resend_verification_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = get_object_or_404(CusUser, email=email)

        if user.is_active:
            messages.success(request, "user is already verified!!!")
            return redirect("a:login")

        current_site = get_current_site(request).domain
        protocol = "https" if request.is_secure() else "http"
        email_subject = "Email Verification"
        message2 = render_to_string(
            "emails/email_verification.html",
            {
                "user": user,
                "domain": current_site,
                "protocol": protocol,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.send(fail_silently=True)

        return redirect("a:login")
    return render(request, "login.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CusUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CusUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully")
        return redirect("a:login")
    else:
        messages.error(request, "Email verification failed")
        return redirect("a:login")


def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("index")


def login(request):
    if request.user.is_authenticated:
        return redirect("url:home")
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("a:login")

        try:
            user = CusUser.objects.get(email=email)
        except CusUser.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect("a:login")

        if not user.is_active:
            messages.error(request, "Please verify your email before logging in.")
            return redirect("a:login")

        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect("u:home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("a:login")

    return render(request, "login.html")


@login_required()
def profile(request, id):
    user_obj = get_object_or_404(CusUser, id=id)

    try:
        profile = user_obj.user_profile_link  # type: ignore
    except UserProfile.DoesNotExist:
        messages.error(request, "user profile does not exist")

    context = {
        "user_obj": user_obj,
        "profile": profile,  # type: ignore
    }
    return render(request, "profile.html", context)


@login_required
def update_profile(request, id):
    profile = request.user.user_profile_link

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        gender = request.POST.get("gender")
        phone_number = request.POST.get("phone_number")
        image = request.FILES.get("profile_image")

        first_name = last_name = ""
        if full_name:
            parts = full_name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        profile.first_name = first_name
        profile.last_name = last_name
        profile.gender = gender
        profile.phone_number = phone_number
        if image:
            profile.profile_image = image

        profile.save()
        return redirect("a:profile", id=id)

    return render(
        request, "profile_setting.html", {"profile": profile, "user_obj": request.user}
    )


@login_required
def update_password(request, id):
    user = get_object_or_404(CusUser, id=id)
    profile = user.user_profile_link  # type: ignore
    context = {
        "user_obj": user,
        "profile": profile,  # type: ignore
    }
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("a:profile", id=id)

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)
        messages.success(request, "Password reset successfully")

        return redirect("a:profile", id=id)

    return render(request, "profile_update_password.html", context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "email is required to reset password")

        try:
            user = CusUser.objects.get(email=email)
            protocol = "https" if request.is_secure() else "http"
            current_site = get_current_site(request)
            email_subject = "reset password"
            message2 = render_to_string(
                "emails/reset_password_email.html",
                {
                    "user": user,
                    "protocol": protocol,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": password_reset_token.make_token(user),
                },
            )

            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.send(fail_silently=True)
            messages.success(request, "Password reset email sent successfully")
            return redirect("a:login")
        except CusUser.DoesNotExist:
            messages.error(request, "User with this email does not exist")
            return redirect("a:forgot_password")
    return render(request, "forgot_password.html")


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CusUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CusUser.DoesNotExist):
        user = None

    if user is not None and password_reset_token.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            confirm_password = request.POST.get("confirm-password")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect("a:reset_password", uidb64=uidb64, token=token)

            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect("a:login")
        return render(request, "reset_password.html", {"user": user})
    else:
        messages.error(request, "Password reset link is invalid or has expired")
        return redirect("a:login")
