from aiogram import Router, types
from aiogram.filters.command import Command

router = Router()


@router.message(Command('help'))
async def bot_help(message: types.Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",
            "/contact - Adminlar bilan aloqa",
            "/about_us - Biz haqimizda"
            )
    await message.answer(text="\n".join(text))
