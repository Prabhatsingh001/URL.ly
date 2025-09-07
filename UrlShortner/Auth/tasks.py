from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.core.mail import EmailMultiAlternatives
from .tokens import password_reset_token
from celery import shared_task


@shared_task
def send_welcome_email(user_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)
    login_url = f"{settings.PROTOCOL}://{settings.SITE_DOMAIN}/a/login/"
    subject = "Welcome to URL.LY"
    html_content = render_to_string(
        "emails/welcome_email.html",
        {
            "user": user,
            "login_url": login_url,
        },
    )
    text_content = (
        f"Hi {user.username},\n\n"
        "Welcome to URL.ly!\n\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n\n"
        f"Login: {login_url}\n\n"
        "If you didn’t sign up, ignore this email.\n\n— URL.ly Team"
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


@shared_task
def send_verification_mail(user_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)
    current_site = settings.SITE_DOMAIN
    protocol = settings.PROTOCOL
    subject = "Confirm your email - URL.LY"
    html_content = render_to_string(
        "emails/email_verification.html",
        {
            "user": user,
            "protocol": protocol,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )

    text_content = f"""
        Hello {user.username},

        Please confirm your email address by clicking the link below:
        {protocol}://{current_site}/a/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_activation_token.make_token(user)}/
        If you did not create an account, please ignore this email.

        Thank you for joining URL.LY!
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


@shared_task
def send_reset_password_email(
    user_id,
    protocol,
    current_site,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)
    subject = "Reset Password"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)
    html_content = render_to_string(
        "emails/reset_password_email.html",
        {
            "user": user,
            "protocol": protocol,
            "domain": current_site,
            "uid": uid,
            "token": token,
        },
    )

    text_content = f"""
        Hello {user.username},
        You have requested to reset your password. Please click the link below to reset it:
        {protocol}://{current_site}/a/reset-password/{uid}/{token}/
        If you did not request this, please ignore this email.
        Thank you for using URL.LY!
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


@shared_task
def password_reset_success_email(user_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)
    subject = "Password Reset Successfully"
    html_content = render_to_string(
        "emails/password_reset_success_email.html",
        {
            "user": user,
            "login_url": f"{settings.PROTOCOL}://{settings.SITE_DOMAIN}/a/login/",
        },
    )

    text_content = f"""
        Hi {user.username},
        Your password has been reset successfully. You can now log in with your new password.
        If you did not request this change, please contact support immediately.
        Thank you for using URL.LY!
    """
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


@shared_task
def send_contact_email(contact_id):
    from .models import Contact

    contact = Contact.objects.get(id=contact_id)
    subject = f"New Notification from {contact.email}"
    html_content = render_to_string(
        "emails/contact_email.html",
        {
            "name": contact.name,
            "email": contact.email,
            "message": contact.message,
        },
    )

    text_content = f"""
        you have recieved a new message

        name: {contact.name}
        email: {contact.email}

        message: {contact.message}
    """
    team_mail = ["ghostcoder420@gmail.com"]

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        team_mail,
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)
