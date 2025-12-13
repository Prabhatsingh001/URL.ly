"""
Utility functions and classes for URL shortening and analytics.

This module provides core functionality for:
- URL slug generation and handling
- QR code generation with custom branding
- Visit analytics and tracking
- Geolocation and user agent parsing
- IP address handling

The utilities handle both the technical aspects of URL shortening
and the analytics gathering for URL visits.
"""

import os
from io import BytesIO

import geoip2.database
import qrcode
import requests
import user_agents
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import FileResponse
from hashids import Hashids
from PIL import Image

hashid = Hashids(min_length=4, salt=settings.SALT)
reader = geoip2.database.Reader("GeoLite2-City.mmdb")


class SlugGenerator:
    """
    Handles encoding and decoding of URL slugs using Hashids.

    This class provides a secure way to generate short URLs from IDs and
    decode them back, using a salt for added security.
    """

    def encode_url(self, id):
        """
        Convert a numeric ID to a short URL slug.

        Args:
            id: Numeric identifier to encode

        Returns:
            str: Encoded slug for use in short URLs
        """
        return hashid.encode(id)

    def decode_url(self, slug: str):
        """
        Convert a URL slug back to its numeric ID.

        Args:
            slug: The encoded URL slug to decode

        Returns:
            tuple: Decoded numeric ID(s)
        """
        return hashid.decode(slug)


class QrCode:
    """
    Handles QR code generation and management for shortened URLs.

    This class manages the creation, storage, and delivery of QR codes,
    including custom branding with a logo overlay.

    Attributes:
        url_instance: The URL model instance to generate QR code for
        request: The HTTP request object for context
    """

    def __init__(self, url_instance, request):
        self.url_instance = url_instance
        self.request = request

    def generate_qr_code(self):
        """
        Generate a QR code for the shortened URL with branded overlay.

        Creates a QR code image with the project logo overlaid in the center,
        saves it to storage, and associates it with the URL instance.
        The QR code includes error correction and custom sizing for optimal scanning.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        full_url = f"{self.request.scheme}://{self.request.get_host()}/u/{self.url_instance.short_url}/"
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")  # type: ignore
        logo_path = os.path.join(settings.BASE_DIR, "static", "logo.png")
        try:
            logo = Image.open(logo_path)
        except FileNotFoundError:
            print("Logo not found at:", logo_path)
            return

        logo_size = 60
        logo = logo.resize((logo_size, logo_size))
        if logo.mode != "RGBA":
            logo = logo.convert("RGBA")

        mask = logo.split()[3] if logo.mode == "RGBA" else None
        qr_width, qr_height = img.size
        offset = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        img.paste(logo, offset, mask=mask)

        buffer = BytesIO()
        img.save(buffer, format="PNG")

        filename = f"{self.url_instance.short_url}_qr.png"
        self.url_instance.qrcode.save(
            filename, ContentFile(buffer.getvalue()), save=True
        )

    def download_qr_code(self):
        """
        Prepare QR code for download as a file attachment.

        Returns:
            FileResponse: HTTP response with QR code image for download

        Generates the QR code if it doesn't exist yet, then prepares it
        for download with proper content type and filename.
        """
        if not self.url_instance.qrcode:
            self.generate_qr_code()

        qr_url = self.url_instance.qrcode.url
        response = requests.get(qr_url, stream=True)
        response.raise_for_status()

        filename = os.path.basename(self.url_instance.qrcode.name)
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filename += ".png"

        return FileResponse(
            BytesIO(response.content),
            as_attachment=True,
            filename=filename,
            content_type="image/png",
        )

    def get_qr_file_to_mail(self):
        """
        mails the qr code to your inbox
        """
        if not self.url_instance.qrcode:
            self.generate_qr_code()

        qr_url = self.url_instance.qrcode.url
        response = requests.get(qr_url, stream=True)
        response.raise_for_status()

        filename = os.path.basename(self.url_instance.qrcode.name)
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filename += ".png"

        return filename, response.content


def get_client_ip(request):
    """
    Extract the client's real IP address from the request.

    Args:
        request: The HTTP request object

    Returns:
        str: The client's IP address, considering proxy forwarding

    Handles both direct client connections and requests through proxies
    by checking the X-Forwarded-For header.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def extract_visit_data(request):
    """
    Extract comprehensive analytics data from a visit request.

    Args:
        request: The HTTP request object

    Returns:
        dict: Visit analytics including:
            - IP address and geolocation data
            - Browser and OS information
            - Device type
            - Bot detection
            - Referrer URL
            - Geographic location (country, region, city)

    Uses GeoIP2 for location lookup and user-agents for device detection.
    """
    ua_string = request.META.get("HTTP_USER_AGENT", "")
    user_agent = user_agents.parse(ua_string)
    ip_address = get_client_ip(request)
    referrer = request.META.get("HTTP_REFERER", None)

    try:
        geo = reader.city(ip_address)
        country = geo.country.name
        region = geo.subdivisions.most_specific.name
        city = geo.city.name
    except Exception:
        country = region = city = None

    return {
        "ip_address": ip_address,
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "device": user_agent.device.family,
        "is_bot": user_agent.is_bot,
        "country": country,
        "region": region,
        "city": city,
        "referrer": referrer,
    }
