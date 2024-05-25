from aiogram.fsm.state import State, StatesGroup


class Post(StatesGroup):
    post = State()

    
class PostToGroup(StatesGroup):
    group_number = State()
    post = State()


class PostToUser(StatesGroup):
    group_number = State()
    student_name = State()
    post = State()
        