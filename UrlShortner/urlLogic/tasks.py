from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from celery import shared_task


@shared_task
def send_qr_email(user_id, filename, filebytes):
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
