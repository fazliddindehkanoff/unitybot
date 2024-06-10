from celery import Celery

app = Celery(
    "my_bot",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

# Assuming tasks.py is in the same directory, or adjust imports accordingly
app.autodiscover_tasks(["."])
