import uuid
import qrcode
from io import BytesIO
from django.core.files import File
# from PIL import Image

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class SlugGenerator:
    def uuid_to_number(self, id):
        # f6f4d690-fd2d-445b-bf9d-14f1726f6ccc
        return id.int

    def encode_url(self, id):
        id = self.uuid_to_number(id)
        if id == 0:
            return BASE62[0]
        result = ""
        while id > 0:
            result = (BASE62[id % 62]) + result
            id //= 62

        return result

    def decode_url(self, slug: str):
        id = 0
        for char in slug:
            id = id * 62 + BASE62.index(char)
        return uuid.UUID(int=id)


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
        full_url = f"{self.request.get_host()}/url/{self.url_instance.short_url}"
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")  # type: ignore

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
