from __future__ import annotations

import logging

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session

import config
from database.db_base import db_base
from database.tables.users_table import User

logger = logging.getLogger(__name__)


class db_helper:
    @staticmethod
    def get_database_session() -> Session:
        logger.debug("Подключение к базе данных")
        engine = db.create_engine(config.DATABASE_ENGINE)

        db_base.Base.metadata.create_all(engine)

        return sessionmaker(bind=engine)()

    session = get_database_session()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        logger.debug(f"Получение пользователя с id = {user_id}")
        return db_helper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def add_new_user(user_id: int, user_full_name: str = "", user_lives_in_b: bool = False, user_room: int = -1) -> None:
        logger.debug(f"Добавление нового пользователя с id = {user_id}")
        new_user = User(user_id=user_id, user_full_name=user_full_name,
                        user_lives_in_b=user_lives_in_b, user_room=user_room)
        db_helper.session.add(new_user)
        db_helper.session.commit()

    @staticmethod
    def set_user_full_name(user_id: int, user_full_name: str):
        logger.debug(f"Установка пользователю с id = {user_id} имя {user_full_name}")
        user = db_helper.get_user_by_id(user_id)
        user.user_full_name = user_full_name
        db_helper.session.commit()

    @staticmethod
    def set_user_lives_in_b(user_id: int, user_lives_in_b: bool):
        logger.debug(f"Установка пользователю с id = {user_id} статус общежития Б: {user_lives_in_b}")
        user = db_helper.get_user_by_id(user_id)
        user.user_lives_in_b = user_lives_in_b
        db_helper.session.commit()

    @staticmethod
    def set_user_room(user_id: int, user_room: int):
        logger.debug(f"Установка пользователю с id = {user_id} номер комнаты {user_room}")
        user = db_helper.get_user_by_id(user_id)
        user.user_room = user_room
        db_helper.session.commit()
