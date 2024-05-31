from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from utils.db.base import Database
from data.config import BOT_TOKEN, DB_USER, DB_PASS, DB_NAME, DB_HOST

db = Database(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
