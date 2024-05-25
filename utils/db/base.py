import sqlite3
from typing import Union


class Database:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NULL,
            last_name TEXT NULL,
            username TEXT,
            telegram_id INTEGER NOT NULL UNIQUE,
            student_id TEXT UNIQUE,
            added_at TEXT,
            guruh TEXT NULL,
            full_name TEXT NULL,
            darajasi TEXT NULL,
            state TEXT NULL
        );
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def add_user(
        self,
        first_name: str,
        last_name: str,
        full_name: None,
        darajasi: None,
        username: Union[str, None],
        telegram_id: int,
        state: str = None,
        student_id: Union[str, None] = None,
        added_at: Union[str, None] = None,
        guruh: Union[str, None] = None,
    ):
        sql = "INSERT INTO Users (first_name, last_name, full_name, darajasi, state, username, telegram_id, student_id, added_at, guruh) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"  # noqa
        self.cursor.execute(
            sql,
            (
                first_name,
                last_name,
                full_name,
                darajasi,
                state,
                username,
                telegram_id,
                student_id,
                added_at,
                guruh,
            ),
        )
        self.conn.commit()

    def select_all_users(self):
        sql = "SELECT * FROM Users"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_user_telegram_id(self, telegram_id: int):
        sql = "SELECT * FROM users WHERE telegram_id = ?"
        self.cursor.execute(sql, (telegram_id,))
        user = self.cursor.fetchone()

        return user

    def get_user_state(self, telegram_id: int):
        sql = "SELECT * FROM users WHERE telegram_id = ?"
        self.cursor.execute(sql, (telegram_id,))
        user = self.cursor.fetchone()
        if user:
            return user[10]
        return ""

    def get_group_for_users(self, group_number: str):
        data = (group_number,)
        sql = "SELECT * FROM Users WHERE guruh = ?"
        self.cursor.execute(sql, data)
        users = self.cursor.fetchall()
        return users

    def is_student_id(self, telegram_id: int) -> bool:
        user = self.get_user_telegram_id(telegram_id)
        if user and user[5] is not None:
            return True
        else:
            return False

    def is_student_full_name(self, telegram_id: int) -> bool:
        user = self.get_user_telegram_id(telegram_id=telegram_id)

        if user and user[8] is not None:
            return True
        else:
            return False

    def check_student_id(self, student_id) -> bool:
        users = self.select_all_users()
        for user in users:
            if user and user[5] == student_id:
                return True
        return False

    def check_student_group(self, user_id):
        users = self.select_all_users()

        for user in users:
            if user and user[7]:
                return user[7]
            else:
                return False

    def update_student_id(self, chat_id, student_id):
        data = (student_id, chat_id)
        sql = "UPDATE Users SET student_id = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def update_state(self, chat_id, state):
        data = (state, chat_id)
        sql = "UPDATE Users SET state = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def update_user_level(self, chat_id, darajasi):
        data = (darajasi, chat_id)
        sql = "UPDATE Users SET darajasi = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def update_user_full_name(self, chat_id, full_name):
        data = (full_name, chat_id)
        sql = "UPDATE Users SET full_name = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def update_group(self, chat_id, group_number):
        data = (group_number, chat_id)
        sql = "UPDATE Users SET guruh = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        conditions = [f"{key} = ?" for key in kwargs.keys()]
        sql += " AND ".join(conditions)
        values = tuple(kwargs.values())
        self.cursor.execute(sql, values)
        return self.cursor.fetchone()

    def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def update_user_username(self, username: str, telegram_id: int):
        sql = "UPDATE Users SET username = ? WHERE telegram_id = ?"
        self.cursor.execute(sql, (username, telegram_id))
        self.conn.commit()

    def delete_users(self):
        sql = "DELETE FROM Users"
        self.cursor.execute(sql)
        self.conn.commit()

    def drop_users(self):
        sql = "DROP TABLE Users"
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()
