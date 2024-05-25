import re

from math import radians, cos, sin, sqrt, atan2
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder


def is_within_radius(lat1, lon1, lat2, lon2, radius_meters):
    # Earth's radius in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Compute differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in meters
    distance = R * c
    print(distance)
    return distance <= radius_meters


def remove_extra_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


async def invite_to_test(current_time, earlier_time, group, db, bot):
    print(f"current_time: {current_time}")
    message = "Hurmatli {}, {} guruhida dars boshlanishiga 30 daqiqa qoldi Test ishlashni unutmang, aks holda bugungi darsga kelmagan deb belgilanasiz\nTest ishlash uchun 1 soat vaqtingiz bor!"  # noqa
    if current_time.strftime("%H:%M") == earlier_time:
        students = db.get_group_for_users(str(group["Guruh raqami"]))
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(
                text="📚Test ishlash",
                callback_data=f"test#{current_time}",
            )
        )
        for student in students:
            await bot.send_message(
                chat_id=student[4],
                text=message.format(student[8], student[7]),
                reply_markup=keyboard.as_markup(),
            )
