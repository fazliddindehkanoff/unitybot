from celery import Celery, shared_task
from loader import groups

app = Celery(
    "my_bot",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

app.conf.beat_schedule = {
    "run-every-second": {
        "task": "tasks.send_telegram_message",
        "schedule": 1.0,  # This sets the task to run every second
    },
}


@shared_task
def send_telegram_message():
    print(groups.col_count)
