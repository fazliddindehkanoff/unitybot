from aiogram.fsm.state import State, StatesGroup


class Userinfo(StatesGroup):
    group_num = State()
    student_name = State()


class UserLocation(StatesGroup):
    location = State()
