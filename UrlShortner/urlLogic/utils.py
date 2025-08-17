import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import os
from django.conf import settings
from hashids import Hashids
from django.http import FileResponse
# from django.core.mail import EmailMultiAlternatives
# from email.mime.image import MIMEImage

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
        buffer.seek(0)

        filename = f"{self.url_instance.short_url}_qr.png"
        self.url_instance.qrcode.save(filename, File(buffer), save=True)

    # def generate_qr_code_bytes(self):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.ERROR_CORRECT_H,
    #         box_size=10,
    #         border=4,
    #     )
    #     full_url = f"{self.request.scheme}://{self.request.get_host()}/url/{self.url_instance.short_url}/"
    #     qr.add_data(full_url)
    #     qr.make(fit=True)

    #     img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    #     buffer = BytesIO()
    #     img.save(buffer, format="PNG")
    #     return buffer.getvalue()

    def download_qr_code(self):
        """
        Return a FileResponse for downloading the QR code
        """
        if not self.url_instance.qrcode:
            self.generate_qr_code()

        qr_path = self.url_instance.qrcode.path
        filename = os.path.basename(qr_path)

        return FileResponse(open(qr_path, "rb"), as_attachment=True, filename=filename)

    def mail_qr_code(self):
        """
        mails the qr code to your inbox
        """
        pass


# def send_qr_mail(user, qr_bytes, short_url):
#     subject = "Your QR Code"
#     text_content = f"Hello {user.username}, your QR code is attached."
#     html_content = f"""
#         <p>Hello {user.username},</p>
#         <p>Here’s your QR code for the link: <b>{short_url}</b></p>
#         <img src="cid:qr_image" />
#     """

#     email = EmailMultiAlternatives(subject, text_content, to=[user.email])
#     email.attach_alternative(html_content, "text/html")

#     qr_img = MIMEImage(qr_bytes, "png")
#     qr_img.add_header("Content-ID", "<qr_image>")
#     email.attach(qr_img)

#     email.send()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
