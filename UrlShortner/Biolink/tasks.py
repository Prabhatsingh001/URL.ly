from celery import shared_task
import time


@shared_task
def generate_qr_async(link_id):
    time.sleep(5)  # simulate heavy work
    print(f"Generated QR for link {link_id}")
    return f"QR code generated for {link_id}"
