from celery import shared_task


@shared_task
def send_telegram_message():
    print("TEST")
