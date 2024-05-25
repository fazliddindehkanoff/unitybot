
import threading
import time
from loader import bot
import datetime
import sqlite3


connection = sqlite3.connect('sqlite3.db')
cursor = connection.cursor()



def send_reminder(user_id):
    bot.send_message(text="Iltimos Test ishlash buyrug'ini berib davomatga yoziling!", chat_id=user_id)
    print(f"O'quvchi IDsi {user_id} ga davomat xabari yuborildi.")

# Avvalgi vaqt
previous_time = None

# Davomat tekshirish va xabar yuborish
while True:
    # Hozirgi vaqt
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    # Agar avvalgi vaqt ma'lum bo'lmagan bo'lsa
    if previous_time is None:
        previous_time = current_time
        continue
    
    # Agar vaqt o'zgardi bo'lsa
    if current_time != previous_time:
        previous_time = current_time
        
        # SQL so'rovi
        sql_query = """
            SELECT user_id, lesson_time 
            FROM userlar
            WHERE lesson_time <= DATETIME('now', '-30 minutes');
        """
        
        # SQL so'rovini bajarish
        cursor.execute(sql_query, (current_time,))
        result = cursor.fetchall()

        # O'quvchilarga xabar yuborish
        for row in result:
            user_id = row[4]
            send_reminder(user_id)
    
    # Kutish uchun 1 sekund
    time.sleep(1)

# def check_lesson_times():
#     while True:
#         # Dars vaqtlari va ulardan oldin yuborilishi kerak bo'lgan vaqt
#         lesson_times = [("09:00", "Dars boshlanmoqda!")]

#         current_time = time.strftime("%H:%M")  # Joriy vaqt
#         for lesson_time, message in lesson_times:
#             # Agar joriy vaqt dars vaqti yarim soat oldin bo'lsa
#             if current_time == lesson_time:
#                 bot.send_message(chat_id="CHAT_ID", text=message)
#         time.sleep(30)  # 30 sekund kutamiz, keyin tekshirishni qayta boshlaymiz