from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

do_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Davomatga qo'shish", callback_data='davomatga_add')],
        [InlineKeyboardButton(text="📨 Xabar jo'natish", callback_data='send_message')],
        [InlineKeyboardButton(text="🗑  O'chirish", callback_data='delete')]
    ]
)