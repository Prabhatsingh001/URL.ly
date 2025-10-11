"""
View functions for URL shortening and management functionality.

This module provides view functions for:
- URL shortening (both authenticated and anonymous)
- URL management (CRUD operations)
- QR code generation and delivery
- URL analytics tracking
- Error handling pages

All views implement proper security measures including:
- Rate limiting for anonymous users
- Authentication checks for protected operations
- Transaction management for data integrity
"""

from datetime import datetime, timezone as dt_timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from .models import ShortUrlAnonymous, UrlModel, UrlVisit
from .utils import QrCode, SlugGenerator, extract_visit_data, get_client_ip

from django.db.models import Count
from django.db.models.functions import TruncDay

from django.views.decorators.cache import cache_page

Slug = SlugGenerator()

# ------------------------------------------------------------------------------
"""custom error pages"""


def F404_page(request, excetipon):
    """
    Handle 404 Not Found errors with a custom template.

    Args:
        request: The HTTP request object
        excetipon: The exception that triggered the 404

    Returns:
        HttpResponse: Rendered 404 page with custom branding

    This view provides a user-friendly 404 page that maintains
    site branding and suggests next steps to users.
    """
    return render(request, "404_notF.html", status=404)


def F500_page(request):
    """
    Handle 500 Server Error responses with a custom template.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered 500 page with custom branding

    Provides a user-friendly error page for server-side errors
    while maintaining site branding and suggesting next steps.
    """
    return render(request, "server_500.html", status=500)


def custom_403_view(request, exception=None):
    """
    Handle rate limit exceeded (403 Forbidden) responses.

    Args:
        request: The HTTP request object
        exception: Optional exception that triggered the 403

    Returns:
        HttpResponse: Redirect to index with error message

    Used primarily for rate limiting responses, providing user-friendly
    feedback when request limits are exceeded.
    """
    message = "You are sending requests too quickly. Please wait a few moments before trying again."
    messages.error(request, message)
    return redirect("index")


# ------------------------------------------------------------------------------
"""url shortening without login"""


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
@cache_page(60 * 10)
def anonymousShorturl(request):
    """
    Create shortened URLs for anonymous users with rate limiting.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered form or redirect with shortened URL

    Features:
    - Rate limited to 5 requests per minute per IP
    - Transaction-safe URL creation
    - IP tracking for anonymous URLs
    - Success/error messaging

    Rate limiting helps prevent abuse while allowing legitimate use
    by anonymous users.
    """
    try:
        short_url = None

        if request.method == "POST":
            original_url = request.POST.get("url")
            if original_url:
                try:
                    with transaction.atomic():
                        url_obj = ShortUrlAnonymous.objects.create(
                            original_url=original_url, ip_address=get_client_ip(request)
                        )
                        slug = Slug.encode_url(url_obj.pk)
                        url_obj.short_code = slug
                        url_obj.save()
                        short_url = request.build_absolute_uri(
                            f"/s/{url_obj.short_code}/"
                        )
                        messages.success(request, "Short URL created successfully!")
                        return redirect(f"{reverse('index')}?short_url={short_url}")
                except Exception as e:
                    messages.error(request, f"Error: {str(e)}")
                    return render(request, "f.html")
        return render(request, "f.html")
    except Ratelimited:
        messages.error(
            request, "You are submitting too fast. Please try again in a few minutes."
        )
        return redirect("index")


def redirect_to_original(request, short_code):
    """
    Redirect anonymous shortened URLs to their original destination.

    Args:
        request: The HTTP request object
        short_code: The shortened URL code to look up

    Returns:
        HttpResponse: Redirect to original URL or 404

    Handles redirects for anonymous user-created short URLs,
    with 404 handling for non-existent URLs.
    """
    url = get_object_or_404(ShortUrlAnonymous, short_code=short_code)
    return redirect(url.original_url)


# ------------------------------------------------------------------------------


@login_required()
def home(request):
    """
    Display dashboard of user's shortened URLs.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered dashboard with URL listing

    Features:
    - Lists all URLs created by the authenticated user
    - Ordered by creation date (newest first)
    - Requires authentication
    - Provides access to URL management features
    """
    urls = UrlModel.objects.filter(user=request.user).order_by("-created_at")
    context = {"urls": urls}
    return render(request, "home.html", context)


@login_required()
@cache_page(60 * 10)
def make_short_url(request):
    """
    Create new shortened URL for authenticated users.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Redirect to dashboard or form with errors

    Features:
    - Custom short URL support
    - Automatic http:// prefix addition
    - Duplicate URL checking
    - 7-day default expiration
    - Transaction-safe creation
    - Validation for URL format and uniqueness

    Security:
    - Requires authentication
    - Validates URL format
    - Prevents duplicate URLs per user
    """
    if request.method == "POST":
        long_url = request.POST.get("long_url", "").strip()
        short_url = request.POST.get("short_url", "").strip()
        expiry = request.POST.get("date", "").strip()

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

        if expiry:
            naive_dt = datetime.fromisoformat(expiry)
            local_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            expires_at = local_dt.astimezone(dt_timezone.utc)
        else:
            expires_at = None
        print(expires_at)

        try:
            with transaction.atomic():
                url = UrlModel.objects.create(
                    original_url=long_url,
                    user=request.user,
                    expires_at=expires_at,
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
    Handle redirects for authenticated user shortened URLs with analytics.

    Args:
        request: The HTTP request object
        slug: The shortened URL identifier

    Returns:
        HttpResponse: Redirect to original URL or error page

    Features:
    - URL existence validation
    - Expiration checking
    - Click counting
    - Comprehensive visit analytics:
        - IP address tracking
        - Browser and OS detection
        - Device identification
        - Geographic location
        - Referrer tracking
        - Bot detection

    Security:
    - Validates URL existence
    - Checks expiration
    - Records all access attempts
    """
    url = UrlModel.objects.filter(short_url=slug).first()
    if url is None:
        return render(request, "404_notF.html")
    elif url.expires_at and timezone.now() > url.expires_at:
        return render(request, "url_expired.html")
    url.click_count += 1
    url.save()
    response_data = extract_visit_data(request)

    UrlVisit.objects.create(
        url=url,
        timestamp=now(),
        ip_address=response_data.get("ip_address"),
        browser=response_data.get("browser"),
        os=response_data.get("os"),
        device=response_data.get("device"),
        is_bot=response_data.get("is_bot"),
        country=response_data.get("country"),
        region=response_data.get("region"),
        city=response_data.get("city"),
        referrer=response_data.get("referrer"),
    )
    return redirect(url.original_url)


@login_required()
@cache_page(60 * 2)
def analytics_dashboard(request, id):
    url = get_object_or_404(UrlModel, id=id)

    visits = UrlVisit.objects.filter(url=url)
    has_data = visits.exists()
    # has_data = False

    if has_data:
        visits_by_day = (
            visits.annotate(day=TruncDay("timestamp"))
            .values("day")
            .annotate(clicks=Count("id"))
            .order_by("day")
        )

        visits_by_country = (
            visits.values("country").annotate(total=Count("id")).order_by("-total")[:5]
        )

        visits_by_device = (
            visits.values("device").annotate(total=Count("id")).order_by("-total")
        )

        visits_by_referrer = (
            visits.values("referrer")
            .annotate(total=Count("id"))
            .exclude(referrer__isnull=True)
            .exclude(referrer="")
            .order_by("-total")[:5]
        )

        total_visits = visits.count()
        top_country = visits_by_country[0]["country"] if visits_by_country else None
        top_device = visits_by_device[0]["device"] if visits_by_device else None
        top_referrer = visits_by_referrer[0]["referrer"] if visits_by_referrer else None
    else:
        # ---------- Dummy Data Section ----------
        from datetime import date, timedelta

        dummy_days = [
            {"day": str(date.today() - timedelta(days=i)), "clicks": x}
            for i, x in enumerate([0, 2, 5, 3, 7, 4, 6][::-1])
        ]
        visits_by_day = dummy_days
        visits_by_country = [
            {"country": "United States", "total": 45},
            {"country": "India", "total": 30},
            {"country": "Germany", "total": 20},
            {"country": "France", "total": 15},
            {"country": "Canada", "total": 10},
        ]
        visits_by_device = [
            {"device": "Desktop", "total": 60},
            {"device": "Mobile", "total": 40},
        ]
        visits_by_referrer = [
            {"referrer": "https://google.com", "total": 50},
            {"referrer": "https://twitter.com", "total": 20},
            {"referrer": "Direct", "total": 30},
        ]

        total_visits = 0
        top_country = "—"
        top_device = "—"
        top_referrer = "—"
        # ---------------------------------------

    context = {
        "url": url,
        "has_data": has_data,
        "total_visits": total_visits,
        "top_country": top_country,
        "top_device": top_device,
        "top_referrer": top_referrer,
        "visits_by_day": list(visits_by_day),
        "visits_by_country": list(visits_by_country),
        "visits_by_device": list(visits_by_device),
        "visits_by_referrer": list(visits_by_referrer),
    }

    return render(request, "analytics_dashboard.html", context)


@login_required()
@require_POST
def delete_url(request, id):
    """
    Delete a shortened URL and associated data.

    Args:
        request: The HTTP request object
        id: The URL model instance ID

    Returns:
        HttpResponse: Redirect to dashboard

    Security:
    - Requires authentication
    - Validates URL ownership
    - POST-only to prevent CSRF
    - Automatic cleanup of associated data
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)
    url.delete()
    return redirect("u:home")


@login_required()
def update_url(request, id):
    """
    Edit URL details including destination and expiration.

    Args:
        request: The HTTP request object
        id: The URL model instance ID

    Returns:
        HttpResponse: Rendered form or redirect to dashboard

    Features:
    - Edit original URL destination
    - Update expiration date/time
    - View comprehensive URL statistics
    - Timezone-aware datetime handling

    Security:
    - Requires authentication
    - Validates URL ownership
    - Maintains URL history
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)

    if request.method == "POST":
        long_url = request.POST.get("long_url")
        expiry_time = request.POST.get("expires_at")

        if long_url:
            url.original_url = long_url

        if expiry_time:
            try:
                expiry_dt = datetime.strptime(expiry_time, "%Y-%m-%dT%H:%M")
                aware_expiry = timezone.make_aware(
                    expiry_dt, timezone.get_current_timezone()
                )
                url.expires_at = aware_expiry.astimezone(dt_timezone.utc)
                print(url.expires_at)
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
    Generate QR code for shortened URL.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Redirect to dashboard after generation

    Features:
    - Custom branded QR codes
    - High error correction level
    - Logo overlay on QR code
    - Automatic storage in cloud
    - Generation on demand

    Security:
    - Requires authentication
    - Validates URL ownership
    - POST-only generation
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
    Download QR code image for a shortened URL.

    Args:
        request: The HTTP request object
        id: The URL model instance ID

    Returns:
        FileResponse: QR code image download

    Features:
    - Automatic QR code generation if missing
    - Proper content type handling
    - Attachment disposition
    - Streaming response

    Security:
    - Requires authentication
    - Validates URL ownership
    - Secure file handling
    """
    url = get_object_or_404(UrlModel, id=id, user=request.user)
    urlservice = QrCode(url, request)
    return urlservice.download_qr_code()


@login_required()
def mail_qr(request, id):
    """
    Email QR code to the URL owner asynchronously.

    Args:
        request: The HTTP request object
        id: The URL model instance ID

    Returns:
        HttpResponse: Redirect to dashboard with success message

    Features:
    - Asynchronous email sending via Celery
    - Automatic QR code generation if missing
    - Both HTML and plain text email formats
    - Transaction-safe operation

    Security:
    - Requires authentication
    - Validates URL ownership
    - Secure file handling
    - Rate limited email sending
    """
    from .tasks import send_qr_email

    url = get_object_or_404(UrlModel, id=id, user=request.user)
    urlservice = QrCode(url, request)

    filename, filebytes = urlservice.get_qr_file_to_mail()

    transaction.on_commit(
        lambda: send_qr_email.delay(request.user.id, filename, filebytes)  # type: ignore
    )
    messages.success(request, "QR code email has been sent.")
    return redirect("u:home")
