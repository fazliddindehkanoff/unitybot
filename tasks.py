from datetime import datetime, timedelta
from celery import Celery, shared_task
import pandas

from loader import bot, db, groups
from utils.extra_datas import invite_to_test

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
async def notify_students():
    current_time = datetime.now()
    today_day_number = current_time.weekday()
    day_names = {
        "Du": 0,
        "Se": 1,
        "Chor": 2,
        "Pay": 3,
        "Ju": 4,
        "Shan": 5,
        "Ya": 6,
        "Har kuni": 99,
    }

    groups_dataframe = pandas.DataFrame(groups.get_all_records())
    for _, group in groups_dataframe[
        groups_dataframe["Status"] == "Boshlangan"
    ].iterrows():
        lesson_time = datetime.strptime(
            str(group["Vaqti"]).split("-")[0],
            "%H:%M",
        )
        earlier_time = (lesson_time - timedelta(minutes=30)).strftime("%H:%M")
        lesson_days = str(group["Kunlari"]).split("-")
        lesson_days_in_number = [day_names[day] for day in lesson_days]

        if "Har kuni" in lesson_days:
            await invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )
            print("har kuni shu vaqtda jo'natilishi kerak")
            print(earlier_time)

        if today_day_number in lesson_days_in_number:
            await invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )
