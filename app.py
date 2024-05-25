import os
import asyncio
import asyncpg

from aiogram import Bot, Dispatcher
from aiogram.client.session.middlewares.request_logging import logger
from loader import db
from handlers.users.start import schedule_notifications


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

    logger.info("Database connected")
    await database_connected()

    logger.info("Starting polling")
    await setup_aiogram(bot=bot, dispatcher=dispatcher)
    await on_startup_notify(bot=bot)
    await set_default_commands(bot=bot)
    logger.info("Notify students starting...")
    asyncio.create_task(schedule_notifications())


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