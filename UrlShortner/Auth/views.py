"""Auth views for URL.ly.

This module implements all user-facing authentication and profile views used by
the application: signup, login, logout, email verification, password reset,
contact form, and profile management. Several views trigger asynchronous
background tasks (Celery) to send emails: verification, contact notifications,
and password reset flows.

Each view accepts a Django HttpRequest and returns an HttpResponse (or a
redirect). Views that modify user data are protected with authentication where
appropriate.
"""

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    update_session_auth_hash,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
import logging

from .models import Contact, UserProfile
from .tasks import (
    password_reset_success_email,
    send_contact_email,
    send_reset_password_email,
    send_verification_mail,
)
from .tokens import account_activation_token, password_reset_token

User = get_user_model()

logger = logging.getLogger("Auth")


def health(request):
    return JsonResponse({"status": "ok"})


class IndexView(View):
    """Landing page view.

    GET: If the user is authenticated redirect to the dashboard (`u:home`).
    Otherwise render the public index page. If `short_url` is present in the
    query parameters it will be passed to the template for pre-filling / display.
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("u:home")
        short_url = request.GET.get("short_url")
        return render(request, "index.html", {"short_url": short_url})


class AboutView(TemplateView):
    """Static about page.

    Renders the `about.html` template. Kept as a TemplateView for simplicity.
    """

    template_name = "about.html"


def contact(request):
    """Handle contact form submissions.

    POST: Validate required fields (name, email, message). On success create a
    Contact object and schedule `send_contact_email` as a background task. Adds
    a success or error message and redirects back to the contact page.

    GET: Render the contact page.

    Args:
        request (HttpRequest): Django request object.

    Returns:
        HttpResponse: Rendered contact page or redirect after POST.
    """

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            contact = Contact.objects.create(name=name, email=email, message=message)
            transaction.on_commit(lambda: send_contact_email.delay(contact.id))  # type: ignore
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("a:contact")
        else:
            messages.error(request, "All fields are required.")
    return render(request, "contact.html")


def signup(request):
    """Register a new user and send verification email.

    POST: Validate the provided username, email and password. If validation
    passes, create an inactive user and schedule an email verification task.
    Adds success/error messages and redirects accordingly.

    GET: Render the signup form.

    Args:
        request (HttpRequest): Django request object.

    Returns:
        HttpResponse: Rendered signup form or redirect after successful POST.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("confirm-password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "email already exists")
            return redirect("a:signup")

        if password != password2:
            messages.error(request, "passwords do not match")
            return redirect("a:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect("a:signup")

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("a:signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.set_password(password)
        user.is_active = False
        user.save()
        transaction.on_commit(lambda: send_verification_mail.delay(user.id))  # type: ignore
        messages.success(
            request, "User created successfully, please verify your email before login"
        )
        return redirect("a:resend-verification-email", email=email)
    return render(request, "signup.html")


def resend_verification_email(request, email=None):
    """Resend account verification email.

    POST: Look up the user by email and, if the account is not active, schedule
    a new verification email. Redirect and flash messages are used to notify
    the user of the result.

    GET: Render the resend verification page with an optional pre-filled
    `email` parameter.
    """

    if request.method == "POST":
        email = request.POST.get("email")
        user = get_object_or_404(User, email=email)

        if user.is_active:
            messages.success(request, "User is already verified!")
            return redirect("a:login")

        transaction.on_commit(lambda: send_verification_mail.delay(user.id))  # type: ignore
        messages.success(request, "Verification email has been resent!")
        return redirect("a:resend-verification-email", email=email)
    return render(request, "resend_verification_email.html", {"email": email})


def activate(request, uidb64, token):
    """Activate a user's account using a uid and token from email link.

    The `uidb64` is base64-encoded user id used together with a token to
    validate the request. On successful validation the account is activated
    and the user is redirected to the login page with a success message.

    Args:
        request (HttpRequest): Django request.
        uidb64 (str): Base64-encoded user id from the activation email.
        token (str): Activation token to validate the request.

    Returns:
        HttpResponse: Redirect to login with success/error message.
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully")
        return redirect("a:login")
    else:
        messages.error(request, "Email verification failed")
        return redirect("a:login")


def login(request):
    """Authenticate and log a user in.

    GET: Render the login page (optionally with a `next` query parameter).

    POST: Validate credentials (email and password). Ensures the account is
    active before authenticating. On success logs the user in and redirects to
    `next` if provided, otherwise to `u:home`.

    Args:
        request (HttpRequest): Django request object.

    Returns:
        HttpResponse: Rendered login page or redirect after authentication.
    """

    if request.user.is_authenticated:
        return redirect("u:home")
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or request.GET.get("next")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("a:login")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect("a:login")

        if not user.is_active:
            messages.error(request, "Please verify your email before logging in.")
            return redirect("a:login")

        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Logged in successfully.")
            if next_url and next_url != "/":
                return redirect(next_url)
            else:
                return redirect("u:home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("a:login")
    next_url = request.GET.get("next", "")
    context = {"next": next_url}
    return render(request, "login.html", context)


def logout(request):
    """Log the current user out and redirect to the index page.

    Args:
        request (HttpRequest): Django request object.
    """

    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("index")


def forgot_password(request):
    """Initiate a password reset by sending an email with a reset link.

    POST: Accepts an `email` field, looks up the user and schedules a
    `send_reset_password_email` task that will email a reset link containing a
    uid and token. Shows success or error messages and redirects to the
    appropriate page.

    GET: Render the "forgot password" form.
    """

    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "email is required to reset password")

        try:
            user = User.objects.get(email=email)
            protocol = "https" if request.is_secure() else "http"
            current_site = get_current_site(request)

            transaction.on_commit(
                lambda: send_reset_password_email.delay(  # type: ignore
                    user.id,  # type: ignore
                    protocol,
                    current_site.domain,
                )
            )

            messages.success(request, "Password reset email sent successfully")
            return redirect("a:login")
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist")
            return redirect("a:forgot_password")
    return render(request, "forgot_password.html")


def reset_password(request, uidb64, token):
    """Complete a password reset after following the emailed link.

    The link contains a base64-encoded user id (`uidb64`) and a `token`. If
    the token validates the user can set a new password. Upon success, a
    confirmation email is scheduled and the user is redirected to login.

    Args:
        request (HttpRequest): Django request object.
        uidb64 (str): Base64-encoded user id.
        token (str): Password reset token.

    Returns:
        HttpResponse: Render reset form or redirect after password reset.
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
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
            transaction.on_commit(lambda: password_reset_success_email.delay(user.id))  # type: ignore
            messages.success(request, "Password reset successfully")
            return redirect("a:login")
        return render(request, "reset_password.html", {"user": user})
    else:
        messages.error(request, "Password reset link is invalid or has expired")
        return redirect("a:login")


@login_required()
def profile(request, id):
    """Show a user's profile.

    Requires the requesting user to be authenticated. Fetches the requested
    `User` by id and passes the related `UserProfile` to the `profile.html`
    template. If no profile exists an error message is flashed.

    Args:
        request (HttpRequest): Django request object.
        id (uuid): Primary key of the requested user.

    Returns:
        HttpResponse: Rendered profile page.
    """

    user_obj = get_object_or_404(User, id=id)

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
    """Update the authenticated user's profile.

    POST: Accepts profile fields (`full_name`, `gender`, `phone_number`, and an
    uploaded `profile_image`) and updates the `UserProfile` linked to the
    authenticated user. After saving redirects back to the profile page.

    GET: Render the profile settings form.

    Args:
        request (HttpRequest): Django request object.
        id (uuid): User id (used for redirect after successful update).

    Returns:
        HttpResponse: Rendered profile settings page or redirect after POST.
    """

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
    """Change a user's password while preserving the session.

    POST: Validate `password` and `confirm-password`, update the user's
    password and refresh the session auth hash so the user remains logged in.
    A success email is scheduled after the change.

    GET: Render the password update form.
    """

    user = get_object_or_404(User, id=id)
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
        # send success email
        transaction.on_commit(lambda: password_reset_success_email.delay(user.id))  # type: ignore
        messages.success(request, "Password reset successfully")

        return redirect("a:profile", id=id)

    return render(request, "profile_update_password.html", context)
