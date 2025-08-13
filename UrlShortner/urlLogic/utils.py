import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import os
from django.conf import settings
from hashids import Hashids

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

hashid = Hashids(min_length=4, salt=settings.SALT)


class SlugGenerator:
    # def uuid_to_number(self, id):
    #     # f6f4d690-fd2d-445b-bf9d-14f1726f6ccc
    #     return id.int

    # def encode_url(self, id):
    #     id = self.uuid_to_number(id)
    #     if id == 0:
    #         return BASE62[0]
    #     result = ""
    #     while id > 0:
    #         result = (BASE62[id % 62]) + result
    #         id //= 62

    #     return result

    # def decode_url(self, slug: str):
    #     id = 0
    #     for char in slug:
    #         id = id * 62 + BASE62.index(char)
    #     return uuid.UUID(int=id)

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

        full_url = f"{self.request.scheme}://{self.request.get_host()}/url/{self.url_instance.short_url}"
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")  # type: ignore
        # logo_path = os.path.join(settings.STATIC_ROOT, "logo.png")
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
        buffer.seek(0)

        filename = f"{self.url_instance.short_url}_qr.png"
        self.url_instance.qrcode.save(filename, File(buffer), save=True)

    def download_qr_code(self, qr_code):
        pass

    def get_qr_code(self):
        pass

    def delete_qr_code(self):
        pass


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
