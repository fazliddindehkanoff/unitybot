from typing import Union
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    darajasi = Column(String, nullable=True)
    state = Column(String, nullable=True)
    username = Column(String, nullable=True)
    telegram_id = Column(String, unique=True)
    student_id = Column(String, unique=True)
    added_at = Column(String, nullable=True)
    guruh = Column(String, nullable=True)


class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_table_users(self):
        Base.metadata.create_all(self.engine)

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
        user = User(
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            darajasi=darajasi,
            username=username,
            telegram_id=telegram_id,
            state=state,
            student_id=student_id,
            added_at=added_at,
            guruh=guruh,
        )
        session = self.Session()
        session.add(user)
        session.commit()

    def select_all_users(self):
        session = self.Session()
        return session.query(User).all()

    def get_user_telegram_id(self, telegram_id: int):
        session = self.Session()
        return session.query(User).filter_by(telegram_id=telegram_id).first()

    def get_user_state(self, telegram_id: int):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            return user.state
        return ""

    def get_group_for_users(self, group_number: str):
        session = self.Session()
        return session.query(User).filter_by(guruh=group_number).all()

    def is_student_id(self, telegram_id: int) -> bool:
        user = self.get_user_telegram_id(telegram_id)
        if user and user.student_id is not None:
            return True
        else:
            return False

    def is_student_full_name(self, telegram_id: int) -> bool:
        user = self.get_user_telegram_id(telegram_id=telegram_id)
        if user and user.full_name is not None:
            return True
        else:
            return False

    def check_student_id(self, student_id) -> bool:
        session = self.Session()
        return (
            session.query(User).filter_by(student_id=student_id).first()
            is not None  # noqa
        )

    def check_student_group(self, user_id):
        session = self.Session()
        user = session.query(User).filter_by(id=user_id).first()
        if user and user.guruh:
            return user.guruh
        else:
            return False

    def update_student_id(self, chat_id, student_id):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=chat_id).first()
        if user:
            user.student_id = student_id
            session.commit()

    def update_state(self, chat_id, state):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=chat_id).first()
        if user:
            user.state = state
            session.commit()

    def update_user_level(self, chat_id, darajasi):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=chat_id).first()
        if user:
            user.darajasi = darajasi
            session.commit()

    def update_user_full_name(self, chat_id, full_name):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=chat_id).first()
        if user:
            user.full_name = full_name
            session.commit()

    def update_group(self, chat_id, group_number):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=chat_id).first()
        if user:
            user.guruh = group_number
            session.commit()

    def select_user(self, **kwargs):
        session = self.Session()
        return session.query(User).filter_by(**kwargs).first()

    def count_users(self):
        session = self.Session()
        return session.query(User).count()

    def update_user_username(self, username: str, telegram_id: int):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.username = username
            session.commit()

    def delete_users(self):
        session = self.Session()
        session.query(User).delete()
        session.commit()

    def drop_users(self):
        Base.metadata.drop_all(self.engine)

    def close(self):
        self.Session().close()
