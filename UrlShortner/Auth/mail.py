"""
Email functionality module for the Auth system.

This module handles all email communications for the authentication and user management system,
including welcome emails, verification emails, password reset notifications, and contact form submissions.
Each email is sent in both HTML and plain text formats for maximum compatibility.

Functions in this module use Django's email backend and template system to generate and send emails.
All email templates are stored in the 'emails' directory within templates.
"""

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token, password_reset_token


def send_welcome_email(user):
    """
    Send a welcome email to newly registered users.

    Args:
        user: The User instance who just registered.

    The email includes:
        - Personalized greeting
        - Login URL
        - User's registration details (username and email)
        - Both HTML and plain text versions
    """
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
        f"Email: {user.email}\n\n" + f"Login: {login_url}\n\n"
        if login_url
        else "" + "If you didn’t sign up, ignore this email.\n\n— URL.ly Team"
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


def send_verification_mail(user):
    """
    Send an email verification link to newly registered users.

    Args:
        user: The User instance whose email needs to be verified.

    The email includes:
        - Verification link with encoded user ID and security token
        - Instructions for verification
        - Both HTML and plain text versions
    """
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


def send_reset_password_email(
    user,
    protocol,
    current_site=settings.SITE_DOMAIN,
):
    """
    Send a password reset link to users who requested it.

    Args:
        user: The User instance requesting password reset
        protocol: The protocol to use in the reset link (http/https)
        current_site: The domain name, defaults to settings.SITE_DOMAIN

    The email includes:
        - Password reset link with encoded user ID and security token
        - Instructions for resetting password
        - Both HTML and plain text versions
    """
    subject = "Reset Password"
    html_content = render_to_string(
        "emails/reset_password_email.html",
        {
            "user": user,
            "protocol": protocol,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": password_reset_token.make_token(user),
        },
    )

    text_content = f"""
        Hello {user.username},
        You have requested to reset your password. Please click the link below to reset it:
        {protocol}://{current_site}/a/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{password_reset_token.make_token(user)}/
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


def password_reset_success_email(user):
    """
    Send a confirmation email after successful password reset.

    Args:
        user: The User instance whose password was reset

    The email includes:
        - Confirmation of password reset
        - Login URL
        - Security warning if user didn't request the change
        - Both HTML and plain text versions
    """
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


def send_contact_email(contact):
    """
    Forward contact form submissions to the team email address.

    Args:
        contact: The Contact instance containing form submission details
                (name, email, and message)

    Sends a notification email to the team with the contact form details.
    Unlike other email functions, this only sends plain text format.
    """
    email_subject = f"New Notofication {contact.email}"
    message = f"""
        you have recieved a new message

        name: {contact.name}
        Email: {contact.email}

        message: {contact.message}
    """
    team_mail = ["ghostcoder420@gmail.com"]

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, team_mail)
    email.send(fail_silently=False)
