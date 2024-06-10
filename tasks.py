from celery import shared_task
from .celery_config import app


@shared_task
def add(x, y):
    return x + y


@shared_task
def send_telegram_message():
    print("testing")
