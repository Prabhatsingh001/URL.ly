from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import UrlModel
from .utils import QrCode, SlugGenerator

Slug = SlugGenerator()
qr = QrCode()


# Create your views here.
@login_required()
def home(request):
    """
    This function retrieves all the URLs from the database and renders them in a template.
    """
    urls = UrlModel.objects.filter(user=request.user).order_by("-created_at")
    context = {"urls": urls}
    return render(request, "home.html", context)


@login_required()
def make_short_url(request):
    """
    this function takes long url from the user and generates a short url for it
    """
    if request.method == "POST":
        long_url = request.POST.get("long_url")
        if not long_url:
            messages.error(request, "Please enter a valid URL.")
            return render(request, "url_shortner.html")
        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        existing_url = UrlModel.objects.filter(
            original_url=long_url, user=request.user
        ).first()
        if existing_url:
            messages.error(request, "This URL has already been shortened.")
            return render(request, "url_shortner.html")
        expiry_time = timezone.now() + timedelta(days=7)
        url = UrlModel.objects.create(
            original_url=long_url, user=request.user, expires_at=expiry_time
        )

        id = url.pk
        slug = Slug.encode_url(id=id)
        url.short_url = slug
        url.save()
        return redirect("url:home")
    return render(request, "url_shortner.html")


def redirect_url(request, slug):
    """
    this function takes the short url and redirects to the long url
    """
    url = get_object_or_404(UrlModel, short_url=slug)
    if url is None:
        return render(request, "url_not_found.html")
    # Check if the URL has expired
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


@login_required(login_url="login")
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
    return render(request, "url_update.html", {"url": url})


@login_required(login_url="login")
def generate_qr(request):
    """
    This function generates a QR code for the short URL.
    """
    url = get_object_or_404(UrlModel, id=request.GET.get("id"))
    qr_code = qr.generate_qr_code(url.short_url)
    context = {"qr_code": qr_code, "url": url}
    return render(request, "qr_code.html", context)
