from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import UrlModel
from .utils import QrCode, SlugGenerator
from django.db import transaction

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

        return redirect("url:home")

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
    return redirect(url.original_url)


@login_required()
def delete_url(reuqest, id):
    """
    this function deletes the url from the database
    """
    url = UrlModel.objects.get(id=id)
    url.delete()
    return redirect("url:home")


@login_required()
def update_url(request, id):
    """
    this function updates the url in the database
    """
    url = get_object_or_404(UrlModel, id=id)
    if request.method == "POST":
        long_url = request.POST.get("long_url")
        expiry_time = timezone.now() + timedelta(days=7)
        url.original_url = long_url
        url.expires_at = expiry_time
        url.save()
        return redirect("url:home")
    return render(request, "update_edit_url.html", {"url": url})


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
        return redirect("url:home")
    return render(request, "home.html")


# @login_required()
# def download_qr(request, id):
#     """
#     This function allows the user to download the QR code for the short URL.
#     """
#     response = qr.download_qr_code(qr_code)
#     return redirect(
#         "url:home", {"response": response}
#     )  # adjust the home html for download


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
