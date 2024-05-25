from aiogram import Router

from filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .admins import startadmin, groupusers
    from .users import start, help
    from .errors import error_handler

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start.router.message.filter(ChatPrivateFilter(chat_type=["private"]))

    router.include_routers(
        startadmin.router,
        start.router,
        groupusers.router,
        help.router,
        error_handler.router,
    )

    return router
