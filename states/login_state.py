from aiogram.filters.state import StatesGroup, State

class Login(StatesGroup):
    student_id = State()

