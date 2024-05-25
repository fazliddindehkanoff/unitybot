from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

base_menu = [
    [InlineKeyboardButton(text="📚 Test ishlash", callback_data="tests")],
    [
        InlineKeyboardButton(
            text="⏬Hujjatlarni yuklash",
            callback_data="send_docs",
        )
    ],
    [InlineKeyboardButton(text="📨Xabar yuborish", callback_data="messages")],
]

menu = InlineKeyboardMarkup(inline_keyboard=base_menu)

base = InlineKeyboardBuilder()
base.attach(InlineKeyboardBuilder.from_markup(menu))

message_menu = [
    [InlineKeyboardButton(text="🔔 Hammaga", callback_data="send_all")],
    [InlineKeyboardButton(text="👥 Guruhga", callback_data="send_group")],
    [InlineKeyboardButton(text="🔙 Ortga", callback_data="home")],
]

message_u = InlineKeyboardMarkup(inline_keyboard=message_menu)
