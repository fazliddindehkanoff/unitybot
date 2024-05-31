import datetime
import json

import gspread
import pandas

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram_widgets.pagination import KeyboardPaginator
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import ADMINS
from filters.admin import IsBotAdminFilter
from loader import bot, db
from states.userinfo import Userinfo
from states.test import Test
from states.post_state import Post, PostToGroup
from keyboards.inline.buttons import builder_messages
from keyboards.inline.base_menu import message_u, base
from utils.extra_datas import remove_extra_whitespace


router = Router()

with open("credentials.json", "r") as file:
    key_data = json.load(file)

gc = gspread.service_account_from_dict(key_data)
sh = gc.open("base")

crm = sh.get_worksheet(0)
groups = sh.get_worksheet(2)
tests = sh.get_worksheet(3)


@router.callback_query(
    F.data == "tests",
    lambda callback_query: str(callback_query.from_user.id) in ADMINS,  # noqa
)
async def send_ad_to_users(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Userinfo.group_num)

    if call.message.text != "groups":
        await call.answer(
            "👥Guruhlar",
        )

        dataframe = pandas.DataFrame(groups.get_all_records())

        group_numbers = []
        for _, row in dataframe.iterrows():
            if row["Status"] != "Tugagan":

                group_numbers.append(row["Guruh raqami"])

        buttons = [
            InlineKeyboardButton(
                text=f"Guruh - {i}",
                callback_data=f"test-group:{i}",
            )
            for i in group_numbers
        ]
        buttons.append(
            InlineKeyboardButton(
                text="🏠Asosiy menu",
                callback_data="home",
            )
        )
        paginator = KeyboardPaginator(
            router=router, data=buttons, per_page=20, per_row=2
        )
        await bot.send_message(
            text="Aktiv guruhlar",
            chat_id=call.from_user.id,
            reply_markup=paginator.as_markup(),
        )


@router.callback_query(
    lambda callback_data: callback_data.data.startswith("test-group:")
    and str(callback_data.from_user.id) in ADMINS,
)
async def get_group(callback_data: types.CallbackQuery, state: FSMContext):
    await callback_data.message.edit_reply_markup()

    group_number = int(callback_data.data.split("test-group:")[-1])

    await state.update_data(group_num=group_number)
    await state.set_state(Userinfo.student_name)

    # Fetch the group data
    groups_df = pandas.DataFrame(groups.get_all_records())
    group_data = groups_df[groups_df["Guruh raqami"] == group_number].iloc[0]

    # Extract group information
    teacher = group_data["Ustoz"]
    total_students = group_data["Talaba soni"]
    group_id = group_data["ID"]
    group_num_n = group_data["Guruh raqami"]
    status = group_data["Status"]
    language = group_data["Kurs tili"]
    monthly_payment = group_data["Oylik to'lov"]
    lesson_days = group_data["Kunlari"]
    lesson_time = group_data["Vaqti"]

    # Fetch the student data
    crm_df = pandas.DataFrame(crm.get_all_records())
    group_students_df = crm_df[crm_df["Guruh raqami"] == group_number]

    # Count students based on their status
    status_counts = group_students_df["Status"].value_counts().to_dict()
    gone_students_count = status_counts.get("Gone", 0)
    stopped_students_count = status_counts.get("Stopped", 0)

    # Get list of active students
    active_students = group_students_df[group_students_df["Status"] == "Here"][
        ["ID", "Ism va Familya"]
    ]

    if active_students.empty:
        await callback_data.message.answer("Faol o'quvchilar topilmadi")
        return

    active_students_list = [
        (str(id), student)
        for id, student in zip(
            active_students["ID"],
            active_students["Ism va Familya"],
        )
    ]
    # Create buttons for students
    buttons = [
        InlineKeyboardButton(
            text=student,
            callback_data=f"student:{id}",
        )
        for id, student in active_students_list
    ]

    buttons.append(
        InlineKeyboardButton(
            text="🏠 Asosiy menu",
            callback_data="home",
        )
    )

    paginator = KeyboardPaginator(
        router=router,
        data=buttons,
        per_page=20,
        per_row=2,
    )

    # Send the message with group information and the paginator
    await bot.send_message(
        text=(
            f"📊 Guruh ma'lumotlari\n"
            f"👩‍🏫 O'qituvchi: {teacher}\n"
            f"👩‍🎓 Jami o'quvchilar: {total_students}\n"
            f"🆔 Guruh ID: {group_id}\n"
            f"🔢 Guruh raqami: {group_num_n}\n"
            f"✅ Status: {status}\n"
            f"🇺🇿 Tili: {language}\n"
            f"💲 Oylik to'lovi: {monthly_payment} so'm\n"
            f"⏲ Dars vaqtlari: {lesson_days}\n"
            f"{lesson_time}\n"
            f"O'quvchilar 🔽🔽\n"
            f"To'xtatgan o'quvchilar soni: {stopped_students_count}\n"
            f"Tugatgan o'quvchilar soni: {gone_students_count}\n"
        ),
        chat_id=callback_data.from_user.id,
        reply_markup=paginator.as_markup(),
    )


@router.callback_query(
    lambda callback_data: callback_data.data.startswith("student:"),
    Userinfo.student_name,
)
async def get_user(callback_data: types.CallbackQuery, state: FSMContext):
    student_id = callback_data.data.split("student:")[-1]
    await state.set_state(Test.Q1)

    # Fetch data only once and outside the function if possible
    test_dataframe = pandas.DataFrame(tests.get_all_records())
    crm_dataframe = pandas.DataFrame(crm.get_all_records())

    # Find the student row
    student = crm_dataframe[crm_dataframe["ID"] == student_id].iloc[0]
    daraja = student["Daraja"]

    # Filter tests based on the student's level
    matching_tests = test_dataframe[test_dataframe["darajasi"] == daraja]
    if matching_tests.empty:
        await callback_data.message.answer(
            "There is no question found based on your level"
        )
        return
    random_test = matching_tests.sample().iloc[0]

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="ℹHint",
            callback_data=f"hint_ans:{random_test['id']}",
        )
    )

    user_chat_id = callback_data.from_user.id
    await bot.send_message(
        text=f"{random_test['savol']}",
        chat_id=user_chat_id,
        reply_markup=builder.as_markup(),
    )
    db.update_state(
        user_chat_id,
        f"answer:{random_test['id']}-student_id:{student_id}",
    )


@router.callback_query(
    lambda c: c.data.startswith("hint_ans") and str(c.from_user.id) in ADMINS,
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
    lambda message: db.get_user_telegram_id(telegram_id=message.from_user.id)[
        10
    ].startswith("answer")
    and str(message.from_user.id) in ADMINS,
)
async def question_1(message: types.Message):
    user = db.get_user_telegram_id(telegram_id=message.from_user.id)
    data = user.state.split("-")
    question_id = data[0].split(":")[-1]
    student_id = data[-1].split(":")[-1]

    test_dataframe = pandas.DataFrame(tests.get_all_records())
    correct_answers = (
        test_dataframe[test_dataframe["id"] == int(question_id)]["javoblar"]
        .iloc[0]
        .lower()
    )
    correct_answers_list = [ans.strip() for ans in correct_answers.split(",")]

    user_answer = remove_extra_whitespace(message.text.lower())

    if user_answer in correct_answers_list:
        davomat = sh.get_worksheet(4)
        crm_df = pandas.DataFrame(crm.get_all_records())
        student = crm_df[crm_df["ID"] == student_id]

        if student.empty:
            await message.reply("Student not found.")
            return

        student_name = student["Ism va Familya"].values[0]
        date_time = datetime.datetime.now().strftime("%m/%d/%Y")

        add_user_davomat = {
            "Sana": date_time,
            "FIO": student_name,
            "Telefon raqam": None,
            "Ota yoki onasining raqami": None,
            "Guruh raqami": None,
            "Ustoz": None,
            "Kunlari": None,
            "Vaqti": None,
            "Status": "Present",
            "Bog'lanish natijasi": None,
            "Sabab": None,
        }
        davomat.append_row(list(add_user_davomat.values()))
        db.update_state(message.from_user.id, "state")

        await message.answer(
            "✅ Davomatga muvaffiqiyatli qo'shildi",
            reply_markup=base.as_markup(),
        )
    else:
        await message.answer("😫Test xato ishlandi. Qaytadan urinib ko'ring")


@router.callback_query(F.data == "messages", IsBotAdminFilter(ADMINS))
async def send_message_all(call: types.CallbackQuery, state: FSMContext):

    await call.message.delete()
    builder_messages.adjust(1)

    await call.message.answer(
        "📤Xabar yuborishingiz mumkin",
        reply_markup=message_u,
    )


@router.callback_query(F.data == "send_all", IsBotAdminFilter(ADMINS))
async def send_message_to_users(call: types.CallbackQuery, state: FSMContext):

    await call.message.answer(text="Post xabarni yuboring> ")
    await state.set_state(Post.post)


@router.message(Post.post)
async def get_post(message: types.Message, state: FSMContext):
    counter = 0
    post_content = message.text
    media_file = None
    media_type = "text"

    if message.photo:
        media_file = message.photo[-1].file_id
        post_content = message.caption
        media_type = "photo"

    elif message.video:
        media_file = message.video.file_id
        post_content = message.caption
        media_type = "video"

    # Forward the post to each user
    all_users = db.select_all_users()
    for row in all_users:
        chat_id = row.telegram_id
        try:

            if media_type == "photo":
                await bot.send_photo(
                    chat_id=chat_id, photo=media_file, caption=post_content
                )

            elif media_type == "video":
                await bot.send_video(
                    chat_id=chat_id, video=media_file, caption=post_content
                )

            else:
                # Send only text content if no media file
                await bot.send_message(chat_id=chat_id, text=post_content)
            counter += 1
        except Exception as e:
            # Handle any exceptions, such as users who have blocked the bot
            print(f"Failed to send post to user :{row[4]} {str(e)}")

    await message.reply(
        f"📬Barcha xabarlar yetkazildi! Yetkazilgan xabarlar soni: {counter}",
        reply_markup=base.as_markup(),
    )


@router.callback_query(F.data == "send_group", IsBotAdminFilter(ADMINS))
async def get_groups_number(call: types.CallbackQuery, state: FSMContext):

    await state.set_state(PostToGroup.group_number)
    dataframe = pandas.DataFrame(groups.get_all_records())
    await call.message.edit_reply_markup()
    await call.answer(
        "👥Guruhlar",
    )

    group_numbers = []
    for _, row in dataframe.iterrows():
        if row["Status"] != "Tugagan":

            group_numbers.append(int(row["Guruh raqami"]))

    buttons = [
        InlineKeyboardButton(text=f"Guruh - {i}", callback_data=f"group:{i}")
        for i in group_numbers
    ]
    buttons.append(
        InlineKeyboardButton(
            text="🏠Asosiy menu",
            callback_data="home",
        )
    )
    paginator = KeyboardPaginator(
        router=router,
        data=buttons,
        per_page=20,
        per_row=2,
    )

    await bot.send_message(
        text="Aktiv guruhlar",
        chat_id=call.from_user.id,
        reply_markup=paginator.as_markup(),
    )


@router.callback_query(
    lambda callback_data: callback_data.data.startswith("group:"),
)
async def sending_post(callback_data: types.CallbackQuery, state: FSMContext):
    group_number = int(callback_data.data.split("group:")[-1])
    await state.update_data(group_number=group_number)

    await state.set_state(PostToGroup.post)
    await bot.send_message(
        chat_id=callback_data.from_user.id, text="Post xabaringizni yuboring> "
    )


@router.message(PostToGroup.post)
async def sending_to_users(message: types.Message, state: FSMContext):
    await state.set_state(PostToGroup.post)
    group_data = await state.get_data()
    counter = 0
    group_number_for_post = group_data.get("group_number")

    post_content = message.text
    media_file = None
    media_type = ""

    if message.photo:
        media_file = message.photo[-1].file_id
        post_content = message.caption
        media_type = "photo"

    elif message.video:
        media_file = message.video.file_id
        post_content = message.caption
        media_type = "video"

    # Forward the post to each user
    all_users = db.get_group_for_users(group_number=group_number_for_post)
    for row in all_users:
        chat_id = row[4]

        try:
            if media_type == "photo":
                await bot.send_photo(
                    chat_id=chat_id, photo=media_file, caption=post_content
                )
            elif media_type == "video":
                await bot.send_video(
                    chat_id=chat_id, video=media_file, caption=post_content
                )
            else:
                await bot.send_message(chat_id=chat_id, text=post_content)
            counter += 1
        except Exception as e:
            print(f"Failed to send post to user :{row[4]} {str(e)}")

    response = (
        f"👥 Guruh raqami: {group_number_for_post}\n"
        f"📬 Barcha xabarlar yetkazildi! Yetkazilgan xabarlar soni: {counter}"
    )
    await message.answer(response, reply_markup=base.as_markup())
