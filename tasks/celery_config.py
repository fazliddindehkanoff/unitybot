from celery import Celery

app = Celery(
    "my_bot",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

app.conf.beat_schedule = {
    "run-every-second": {
        "task": "task.celery_tasks.every_second_task",
        "schedule": 1.0,  # This sets the task to run every second
    },
}
