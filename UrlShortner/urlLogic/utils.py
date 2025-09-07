import qrcode
import os
from io import BytesIO
from PIL import Image
from django.conf import settings
from hashids import Hashids
from django.http import FileResponse
from django.core.files.base import ContentFile
import requests

hashid = Hashids(min_length=4, salt=settings.SALT)


class SlugGenerator:
    def encode_url(self, id):
        return hashid.encode(id)

    def decode_url(self, slug: str):
        return hashid.decode(slug)


class QrCode:
    def __init__(self, url_instance, request):
        self.url_instance = url_instance
        self.request = request

    def generate_qr_code(self):
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
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
