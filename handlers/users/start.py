import asyncio
import random
import json

import pandas
import gspread

from datetime import datetime, timedelta
from aiogram import Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

from filters.admin import IsBotAdminFilter
from loader import bot, db
from keyboards.inline.menu_user import location_keyboard
from utils.extra_datas import (
    invite_to_test,
    remove_extra_whitespace,
    is_within_radius,
)
from states.login_state import Login


router = Router()

with open("credentials.json", "r") as file:
    key_data = json.load(file)

gc = gspread.service_account_from_dict(key_data)
sheet = gc.open("base")
crm = sheet.get_worksheet(0)
groups = sheet.get_worksheet(2)
tests = sheet.get_worksheet(3)


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    full_name = message.from_user.full_name
    username = message.from_user.username
    now = datetime.now()
    db.create_table_users()
    if db.get_user_telegram_id(telegram_id=telegram_id):
        if db.is_student_id(telegram_id=telegram_id):
            await message.answer(
                f"""Assalomu alaykum {full_name}!, Bu bot sizga darsingizdan oldin test ishlash uchun habar yuboradi va siz bu test ishlash orqali davomatingiz olinadi"""  # noqa
            )
        else:

            await message.answer(
                f"""Assalomu alaykum {full_name}\n Sizga berilgan login kiritish orqali profilingizga kiring Bir login orqali faqat bitta telegram hisob bilan kira olasiz""",  # noqa
            )
            await state.set_state(Login.student_id)

    else:
        db.add_user(
            first_name=first_name,
            last_name=last_name,
            full_name=None,
            darajasi=None,
            username=username,
            telegram_id=telegram_id,
            student_id=None,
            added_at=now,
        )

        await message.answer(
            f"""Assalomu alaykum {full_name}\nSizga berilgan login kiritish orqali profilingizga kiring Bir login orqali faqat bitta telegram hisob bilan kira olasiz""",  # noqa
        )
        await state.set_state(Login.student_id)


@router.message(Login.student_id)
async def get_login(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.text.lower()
    crm_dateframe = pandas.DataFrame(crm.get_all_records())
    data = crm_dateframe[crm_dateframe["ID"] == user_id]

    if not data.empty:
        group_number = data["Guruh raqami"].values[0]
        status = data["Status"].values[0]

        if status in ["Gone", "Stopped"]:
            await message.answer(
                "Ushbu logindangi foydalanuvchi hozirda o'quv markazimizda o'qimaydi!",  # noqa
            )
        elif db.check_student_id(user_id):
            await message.answer(
                "Siz kiritgan login boshqa telegram hisobga ulangan."
            )  # noqa
        else:
            db.update_student_id(
                chat_id=message.from_user.id,
                student_id=user_id,
            )
            db.update_group(
                chat_id=message.from_user.id,
                group_number=group_number,
            )
            db.update_user_full_name(
                chat_id=message.from_user.id,
                full_name=data["Ism va Familya"].values[0],
            )
            db.update_user_level(
                chat_id=message.from_user.id, darajasi=data["Daraja"].values[0]
            )

            await message.answer(
                "Profilingizga muvaffaqiyatli kirdingiz, Darsingiz bo'ladigan kunlari sizga test ishlash uchun eslatmalar yuborilib turadi"  # noqa
            )


async def notify_students():
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
            await invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )
            print("har kuni shu vaqtda jo'natilishi kerak")
            print(earlier_time)

        if today_day_number in lesson_days_in_number:
            await invite_to_test(
                current_time=current_time,
                earlier_time=earlier_time,
                group=group,
                db=db,
                bot=bot,
            )


async def schedule_notifications():
    print("scheduling notifications function called")
    while True:
        print("while is working")
        await notify_students()
        await asyncio.sleep(60)


@router.callback_query(lambda callback_query: callback_query.data.startswith("test#"))
async def process_callback_test(callback_query: types.CallbackQuery):
    try:
        sending_time_str = callback_query.data.split("#")[1]
        sending_time = datetime.strptime(
            sending_time_str,
            "%Y-%m-%d %H:%M:%S.%f",
        )
        current_time = datetime.now()
        time_difference = current_time - sending_time

        if time_difference > timedelta(minutes=60):
            await bot.answer_callback_query(
                callback_query.id,
                text="Davomatga olish vaqti tugagan.",
                show_alert=True,
            )
            await callback_query.message.delete()

        else:
            await callback_query.message.answer(
                "Iltimos hozirgi turgan joylashuvingizni yuboring",
                reply_markup=location_keyboard,
            )
            db.update_state(callback_query.from_user.id, "check_location")

    except Exception as e:
        print(e)
        await bot.answer_callback_query(
            callback_query.id,
            text="Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
            show_alert=True,
        )


@router.message(
    lambda message: db.get_user_state(message.from_user.id) == "check_location"
    and not IsBotAdminFilter(message.from_user.id)
)
async def check_location(message: types.Message):
    if not message.location:
        response = (
            "Iltimos joylashuvingizni lokatsiya ko'rinishida yuboring, ",
            "Joylashuv manzilingiz o'quv markazimiz 100m radiusida bo'lishi lozim",  # noqa
        )
        await message.answer(response)
        return

    user_lat = message.location.latitude
    user_lon = message.location.longitude

    place_lat = 40.3862
    place_lon = 71.7709
    radius = 100
    user_in_academy = is_within_radius(
        user_lat,
        user_lon,
        place_lat,
        place_lon,
        radius,
    )
    if user_in_academy and message.forward_date is None:
        test_dataframe = pandas.DataFrame(tests.get_all_records())
        user = db.get_user_telegram_id(message.from_user.id)

        question_based_on_level = test_dataframe[
            test_dataframe["darajasi"] == user[9]
        ].values.tolist()

        if not question_based_on_level:
            await message.answer(
                "Siz uchun testlar topilmadi.",
            )
            return

        random_test = random.choice(question_based_on_level)
        db.update_state(
            chat_id=message.from_user.id,
            state=f"answer:{random_test[0]}",
        )
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="ℹHint",
                callback_data=f"hint_ans:{random_test[0]}",
            )
        )

        await message.answer(
            text=f"{random_test[1]}",
            reply_markup=builder.as_markup(),
        )
    elif message.location and message.forward_date:
        await message.reply("Lokatsiyani forward qilish orqali alday olmaysiz")
    else:
        await message.reply("Siz hali markazimiz hududida emas ekansiz!")


@router.callback_query(
    lambda callback_query: callback_query.data.startswith("hint_ans")
    and not IsBotAdminFilter(callback_query.from_user.id)
)
async def hint_answer(call: types.CallbackQuery):
    question_id = call.data.split(":")[-1]
    test_dataframe = pandas.DataFrame(tests.get_all_records())
    question = test_dataframe[test_dataframe["id"] == int(question_id)]

    if not question.empty:
        await call.answer(
            text=str(question["havola"].iloc[0]),
            show_alert=True,
        )
    else:
        await call.answer(text="❌Information not found", show_alert=True)


@router.message(
    lambda message: db.get_user_state(
        telegram_id=message.from_user.id  # noqa
    ).startswith("answer")
    and not IsBotAdminFilter(message.from_user.id)
)
async def question_1(message: types.Message):
    user = db.get_user_telegram_id(telegram_id=message.from_user.id)
    question_id = user[10].split(":")[-1]
    test_dataframe = pandas.DataFrame(tests.get_all_records())
    correct_answers = (
        test_dataframe[test_dataframe["id"] == int(question_id)]["javoblar"]
        .iloc[0]
        .lower()
    )
    correct_answers_list = [ans.strip() for ans in correct_answers.split(",")]

    user_answer = remove_extra_whitespace(message.text.lower())

    if user_answer in correct_answers_list:
        base_groups_dateframe = pandas.DataFrame(groups.get_all_records())
        group_number = int(user[7])
        group_data = base_groups_dateframe[
            base_groups_dateframe["Guruh raqami"] == group_number
        ]
        teacher = group_data["Ustoz"].values[0]
        date = group_data["Kunlari"].values[0]
        time = group_data["Vaqti"].values[0]
        davomat = sheet.get_worksheet(4)

        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y")
        add_user_davomat = {
            "Sana": date_time,
            "FIO": user[8],
            "Telefon raqam": None,
            "Ota yoki onasining raqami": None,
            "Guruh raqami": group_number,
            "Ustoz": teacher,
            "Kunlari": date,
            "Vaqti": time,
            "Status": "Present",
            "Bog'lanish natijasi": None,
            "Sabab": None,
        }
        davomat.append_row(list(add_user_davomat.values()))
        db.update_state(message.from_user.id, "state")

        await message.answer("✅ Davomatga muvaffiqiyatli qo'shildi")

    else:
        await message.answer(
            "😫Test xato ishlandi. Qaytadan urinib ko'ring",
        )
