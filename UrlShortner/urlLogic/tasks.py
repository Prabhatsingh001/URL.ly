"""
Asynchronous Celery tasks for URL-related email notifications.

This module handles background tasks for sending QR code emails to users.
Emails are sent asynchronously to avoid blocking the main application flow
and include both HTML and plain text versions with file attachments.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_qr_email(user_id, filename, filebytes):
    """
    Send an email with a QR code attachment to a user asynchronously.

    Args:
        user_id: UUID of the user to send the email to
        filename: Name of the QR code file to be attached
        filebytes: Binary content of the QR code image

    The email includes:
        - QR code as a PNG attachment
        - HTML and plain text versions of the message
        - Support contact information
        - Branded email template

    Uses qr_code_email.html template for consistent branding and
    sends the email with fail_silently=True to prevent task failures.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)
    subject = "Your QR Code is Ready"
    html_content = render_to_string(
        "email/qr_code_email.html",
        {
            "filename": filename,
            "support_email": settings.SUPPORT_EMAIL,
        },
    )

    text_content = (
        "Your QR Code is ready. Please find the QR code attached.\n\n"
        "If you have any questions, feel free to reach out to us at "
        f"{settings.SUPPORT_EMAIL}.\n\n"
        "Best regards,\n"
        "The URL.ly Team"
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.attach(filename, filebytes, "image/png")
    email.send(fail_silently=True)


@shared_task
def save_url_visit_data(url_id, url_visit_data):
    """
    Save URL visit data asynchronously.

    Args:
        url_id: ID of the UrlModel instance
        url_visit_data: Dictionary containing visit data such as
                        ip_address, browser, os, device, is_bot,
                        country, region, city, referrer

    This task creates a UrlVisit record in the database with the
    provided visit data.
    """
    from .models import UrlModel, UrlVisit
    from django.utils.timezone import now

    url = UrlModel.objects.get(id=url_id)

    UrlVisit.objects.create(
        url=url,
        timestamp=now(),
        ip_address=url_visit_data.get("ip_address"),
        browser=url_visit_data.get("browser"),
        os=url_visit_data.get("os"),
        device=url_visit_data.get("device"),
        is_bot=url_visit_data.get("is_bot"),
        country=url_visit_data.get("country"),
        region=url_visit_data.get("region"),
        city=url_visit_data.get("city"),
        referrer=url_visit_data.get("referrer"),
    )
