from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import UrlModel, UrlVisit
from .utils import QrCode, SlugGenerator
from django.db import transaction
from django.utils.timezone import now
import user_agents
from .utils import get_client_ip
from django.views.decorators.http import require_POST

Slug = SlugGenerator()


def F404_page(request, excetipon):
    """
    This function renders a custom 404 page.
    """
    return render(request, "404_notF.html", status=404)


def F500_page(request):
    """
    This function renders a custom 500 page.
    """
    return render(request, "server_500.html", status=500)


@login_required()
def home(request):
    """
    This function retrieves all the URLs from the database and renders them in a template.
    """
    urls = UrlModel.objects.filter(user=request.user).order_by("-created_at")
    context = {"urls": urls}
    return render(request, "home.html", context)


@login_required
def make_short_url(request):
    if request.method == "POST":
        long_url = request.POST.get("long_url", "").strip()
        short_url = request.POST.get("short_url", "").strip()

        if not long_url:
            messages.error(request, "Please enter a valid URL.")
            return render(request, "url_shortner.html")

        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        if UrlModel.objects.filter(original_url=long_url, user=request.user).exists():
            messages.error(request, "This URL has already been shortened.")
            return render(request, "url_shortner.html")

        if short_url and UrlModel.objects.filter(short_url=short_url).exists():
            messages.error(request, "This short URL already exists. Try another name.")
            return render(request, "url_shortner.html")

        expiry_time = timezone.now() + timedelta(days=7)

        try:
            with transaction.atomic():
                url = UrlModel.objects.create(
                    original_url=long_url,
                    user=request.user,
                    expires_at=expiry_time,
                )

                slug = short_url or Slug.encode_url(id=url.pk)
                if not slug:
                    raise ValueError("Slug generation failed")

                url.short_url = slug
                url.save()

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, "url_shortner.html")

        return redirect("u:home")

    return render(request, "url_shortner.html")


def redirect_url(request, slug):
    """
    this function takes the short url and redirects to the long url
    """
    url = UrlModel.objects.filter(short_url=slug).first()
    if url is None:
        return render(request, "404_notF.html")
    elif url.expires_at and timezone.now() > url.expires_at:
        return render(request, "url_expired.html")
    url.click_count += 1
    url.save()
    ua_string = request.META.get("HTTP_USER_AGENT", "")
    ip = get_client_ip(request)
    ua = user_agents.parse(ua_string)

    UrlVisit.objects.create(
        url=url,
        timestamp=now(),
        ip_address=ip,
        browser=ua.browser.family,
        os=ua.os.family,
        device=ua.device.family,
    )
    return redirect(url.original_url)


@login_required()
@require_POST
def delete_url(request, id):
    """
    Only allow the user to delete their own URL.
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)
    url.delete()
    return redirect("u:home")


@login_required()
def update_url(request, id):
    """
    Show URL details and allow editing of original_url and expiry.
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)

    if request.method == "POST":
        long_url = request.POST.get("long_url")
        expiry_time = request.POST.get("expires_at")

        if long_url:
            url.original_url = long_url

        if expiry_time:
            from datetime import datetime
            from django.utils import timezone

            try:
                expiry_dt = datetime.strptime(expiry_time, "%Y-%m-%dT%H:%M")
                url.expires_at = timezone.make_aware(expiry_dt)
            except ValueError:
                pass
        url.save()
        return redirect("u:home")

    url_details = [
        ("Short URL", url.short_url),
        ("Original URL", url.original_url),
        ("Created At", url.created_at),
        ("Expires At", url.expires_at if url.expires_at else "Never"),
        ("Click Count", url.click_count),
    ]

    return render(
        request, "update_edit_url.html", {"url": url, "url_details": url_details}
    )


@login_required()
def generate_qr(request):
    """
    This function generates a QR code for the short URL.
    """
    if request.method == "POST":
        url_id = request.POST.get("id")
        url = get_object_or_404(UrlModel, id=url_id, user=request.user)
        if not url.qrcode:
            urlservice = QrCode(url, request)
            urlservice.generate_qr_code()
        return redirect("u:home")
    return render(request, "home.html")


@login_required()
def download_qr(request, id):
    """
    This function allows the user to download the QR code for the short URL.
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)
    urlservice = QrCode(url, request)
    return urlservice.download_qr_code()


@login_required()
def mail_qr(request, id):
    from .tasks import send_qr_email

    url = get_object_or_404(UrlModel, id=id, user=request.user)
    urlservice = QrCode(url, request)

    filename, filebytes = urlservice.get_qr_file_to_mail()

    transaction.on_commit(
        lambda: send_qr_email.delay(request.user.id, filename, filebytes)
    )  # type: ignore
    messages.success(request, "QR code email has been sent.")
    return redirect("u:home")
