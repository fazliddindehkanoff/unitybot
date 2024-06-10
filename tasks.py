# tasks.py

from celery import shared_task


@shared_task
def every_second_task():
    print("Task is running every second")
