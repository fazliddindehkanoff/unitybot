import asyncio
import pandas

from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import logger
from celery import Celery, shared_task

from loader import bot, db, groups
from utils.extra_datas import invite_to_test


def setup_handlers(dispatcher: Dispatcher) -> None:
    """HANDLERS"""
    from handlers import setup_routers

    dispatcher.include_router(setup_routers())


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from middlewares.throttling import ThrottlingMiddleware

    # Spamdan himoya qilish uchun klassik ichki o'rta dastur.
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))


def setup_filters(dispatcher: Dispatcher) -> None:
    """FILTERS"""
    from filters import ChatPrivateFilter

    # Chat turini aniqlash uchun klassik umumiy filtr
    # Filtrni handlers/users/__init__
    dispatcher.message.filter(ChatPrivateFilter(chat_type=["private"]))


async def setup_aiogram(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.info("Configuring aiogram")
    setup_handlers(dispatcher=dispatcher)
    setup_middlewares(dispatcher=dispatcher, bot=bot)
    setup_filters(dispatcher=dispatcher)
    logger.info("Configured aiogram")


async def database_connected():
    db.create_table_users()


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify

    await database_connected()
    logger.info("Database connected")

    logger.info("Starting polling")
    await setup_aiogram(bot=bot, dispatcher=dispatcher)
    await on_startup_notify(bot=bot)
    await set_default_commands(bot=bot)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot):
    logger.info("Stopping polling")
    await bot.session.close()
    await dispatcher.storage.close()


def main():
    """CONFIG"""
    from data.config import BOT_TOKEN
    from aiogram.enums import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)

    dispatcher.startup.register(aiogram_on_startup_polling)
    dispatcher.shutdown.register(aiogram_on_shutdown_polling)
    asyncio.run(dispatcher.start_polling(bot, close_bot_session=True))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped!")


app = Celery(
    "my_bot",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

app.conf.beat_schedule = {
    "run-every-second": {
        "task": "app.notify_students",
        "schedule": 1.0,  # This sets the task to run every second
    },
}


@shared_task
def notify_students():
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
            invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )
            print("har kuni shu vaqtda jo'natilishi kerak")
            print(earlier_time)

        if today_day_number in lesson_days_in_number:
            invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )
