from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

builder_messages = ReplyKeyboardBuilder()
builder_messages.row(
    KeyboardButton(text="🔔 Hammaga"),
    KeyboardButton(text="👥 Guruhga"),
    KeyboardButton(text="👤 O'quvchiga"),
    KeyboardButton(text="❌ Bekor qilish"),
)
