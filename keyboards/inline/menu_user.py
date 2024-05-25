from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

user_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📚 Test ishlash",
                callback_data="test_ishlash",
            )
        ],
        [InlineKeyboardButton(text="📑  Hujjatlar", callback_data="documents")],
    ]
)

location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📍 Share Location",
                request_location=True,
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
