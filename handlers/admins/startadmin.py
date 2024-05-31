import gspread
import json
import pandas as pd

from aiogram import Router, types, F
from aiogram.filters import Command

# from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from data.config import ADMINS, BOT_TOKEN
from keyboards.inline.base_menu import base
from loader import bot, db


router = Router()


with open("credentials.json", "r") as file:
    key_data = json.load(file)

gc = gspread.service_account_from_dict(key_data)

sh = gc.open("base")

documents = sh.get_worksheet(1)
pages = len(sh.worksheets())
crm = sh.get_worksheet(0)
groups = sh.get_worksheet(2)
users = sh.get_worksheet(3)


@router.message(
    Command("start"), lambda message: str(message.from_user.id) in ADMINS
)  # noqa
async def get_all_users(message: types.Message):
    groups_dataframe = pd.DataFrame(groups.get_all_records())
    users_dataframe = pd.DataFrame(crm.get_all_records())
    filtered_users = users_dataframe[users_dataframe["Status"] == "Here"]

    available_groups = groups_dataframe.loc[
        groups_dataframe["Status"] == "Boshlangan"
    ].shape[0]
    number_of_active_users = db.count_users()

    response_message = (
        f"Ba'zi statistikalar:\n"
        f"👨‍🎓👩‍🎓Aktiv o'quvchilar soni: {len(filtered_users)}\n"
        f"💎Jami guruhlar soni: {available_groups}\n"
        f"👥Botdagi jami foydalanuvchilar: {number_of_active_users}\n"
    )

    await message.answer(
        response_message,
        reply_markup=base.as_markup(),
    )
    chat_id = message.from_user.id
    if not db.get_user_telegram_id(chat_id):
        db.add_user(
            first_name=message.from_user.first_name,
            last_name=None,
            full_name=None,
            darajasi=None,
            username=message.from_user.username,
            telegram_id=chat_id,
            student_id="Admin",
            added_at=None,
        )


@router.message(
    Command("menu"), lambda message: str(message.from_user.id) in ADMINS
)  # noqa
async def ask_ad_content(message: types.Message):
    await message.answer("Asosiy menu>> ", reply_markup=base.as_markup())


@router.callback_query(
    lambda callback_query: callback_query.data == "home",
    lambda callback_query: str(callback_query.from_user.id) in ADMINS,
)
async def go_home(call: types.CallbackQuery):
    groups_dataframe = pd.DataFrame(groups.get_all_records())
    users_dataframe = pd.DataFrame(crm.get_all_records())
    filtered_users = users_dataframe[users_dataframe["Status"] == "Here"]

    available_groups = groups_dataframe.loc[
        groups_dataframe["Status"] != "Tugagan"
    ].shape[0]
    number_of_active_users = db.count_users()

    await call.message.delete_reply_markup()
    response_message = (
        f"Ba'zi statistikalar:\n"
        f"👨‍🎓👩‍🎓Aktiv o'quvchilar soni: {len(filtered_users)}\n"
        f"💎Jami guruhlar soni: {available_groups}\n"
        f"👥Botdagi jami foydalanuvchilar: {number_of_active_users}\n"
    )
    await call.message.answer(
        response_message,
        reply_markup=base.as_markup(),
    )


@router.message(
    F.text == "◀ Orqaga", lambda message: str(message.from_user.id) in ADMINS
)  # noqa
async def back_to_main_menu(message: types.Message):
    builder = ReplyKeyboardRemove()
    await message.answer(">>>", reply_markup=builder)
    await message.answer("Asosiy menu>> ", reply_markup=base.as_markup())


@router.callback_query(
    F.data == "send_docs", lambda call: str(call.from_user.id) in ADMINS
)
async def get_documents(call: types.CallbackQuery):
    await bot.send_message(
        text="Salom Admin✋ Yuklamoqchi bo'lgan fayllarni menga yuboring..",
        chat_id=call.from_user.id,
    )
    db.update_state(chat_id=call.from_user.id, state="send_docs")


@router.message(
    lambda msg: str(msg.from_user.id) in ADMINS,
    lambda msg: db.get_user_telegram_id(msg.from_user.id)[10] == "send_docs",
)
async def receive_files(message: types.Message):
    try:
        # Get the file information
        file_info = await bot.get_file(message.document.file_id)
        file_path = file_info.file_path

        # Create the file link
        file_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # Use the file name from the message
        file_name = message.document.file_name

        # Add the document information to your documents
        add_document = {"nomi": file_name, "link": file_link}
        documents.append_row(list(add_document.values()))

        # Send a success message
        await message.reply(
            text="✅ Bazaga muvaffiqiyatli joylandi.",
            reply_markup=base.as_markup(),
        )
        db.update_state(chat_id=message.from_user.id, state="state")

    except Exception as e:
        # Handle errors and notify the user
        await message.reply(text=f"❌ Xatolik yuz berdi: {e}")
        print(f"Error occurred: {e}")
