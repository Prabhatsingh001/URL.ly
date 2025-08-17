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


# Create your views here.
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

        # Check if this URL was already shortened by this user
        if UrlModel.objects.filter(original_url=long_url, user=request.user).exists():
            messages.error(request, "This URL has already been shortened.")
            return render(request, "url_shortner.html")

        # Check if custom short URL is already taken
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
    ip = get_client_ip(request)  # Defined below
    ua = user_agents.parse(ua_string)

    # Create a new visit entry
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
            # Convert input datetime-local to Python datetime
            from datetime import datetime
            from django.utils import timezone

            try:
                expiry_dt = datetime.strptime(expiry_time, "%Y-%m-%dT%H:%M")
                url.expires_at = timezone.make_aware(expiry_dt)
            except ValueError:
                pass  # optionally handle invalid input

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


# @login_required
# def mail_qr(request, id):
#     url = get_object_or_404(UrlModel, id=id, user=request.user)
#     qrservice = QrCode(url, request)
#     qr_bytes = qrservice.generate_qr_code_bytes()

#     send_qr_mail(request.user, qr_bytes, url.short_url)
#     # OR send_qr_inline(request.user, qr_bytes, url.short_url)

#     messages.success(request, "QR Code has been sent to your email!")
#     return redirect("u:home")


# @login_required()
# def delete_qr(request, id):
#     """
#     This function deletes the QR code for the short URL.
#     """
#     url = get_object_or_404(UrlModel, id=id)
#     url.qrcode.delete()
#     url.save()
#     messages.success(request, "QR code deleted successfully.")
#     return redirect("url:home")
