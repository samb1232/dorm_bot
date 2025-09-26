from __future__ import annotations

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from database.db_base import db_base
from database.tables.debtors_table import Debtor
from database.tables.users_table import User
from configs.my_logger import get_logger


logger = get_logger(__name__)

DATABASE_ENGINE = "sqlite:///database.db"


class DbHelper:
    logger.debug("Подключение к базе данных")
    engine = db.create_engine(DATABASE_ENGINE)

    db_base.Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        logger.debug(f"Получение пользователя с id = {user_id}")
        return DbHelper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_user_id_by_full_name(full_name: str) -> int | None:
        logger.debug(f"Получение id пользователя с именем {full_name}")
        user = DbHelper.session.query(User).filter(User.full_name == full_name).first()
        if user:
            return user.user_id  # Возвращаем первый элемент кортежа, который содержит id пользователя
        return None

    @staticmethod
    def add_new_user(user_id: int, user_full_name: str = "", user_lives_in_b: bool = False,
                     user_room: int = -1) -> None:
        logger.debug(f"Добавление нового пользователя с id = {user_id}")
        new_user = User(user_id=user_id, full_name=user_full_name,
                        lives_in_b=user_lives_in_b, room_number=user_room)
        DbHelper.session.add(new_user)
        DbHelper.session.commit()

    @staticmethod
    def set_user_full_name(user_id: int, user_full_name: str):
        logger.debug(f"Установка пользователю с id = {user_id} имя {user_full_name}")
        user = DbHelper.get_user_by_id(user_id)
        user.full_name = user_full_name
        DbHelper.session.commit()

    @staticmethod
    def set_user_lives_in_b(user_id: int, user_lives_in_b: bool):
        logger.debug(f"Установка пользователю с id = {user_id} статус общежития Б: {user_lives_in_b}")
        user = DbHelper.get_user_by_id(user_id)
        user.lives_in_b = user_lives_in_b
        DbHelper.session.commit()

    @staticmethod
    def set_user_room(user_id: int, user_room: int):
        logger.debug(f"Установка пользователю с id = {user_id} номер комнаты {user_room}")
        user = DbHelper.get_user_by_id(user_id)
        user.room_number = user_room
        DbHelper.session.commit()

    @staticmethod
    def update_debtors_table(new_debtors: dict):
        logger.debug("Обновление должников в базе данных")
        DbHelper.session.query(Debtor).delete()

        # Добавление новых должников
        for full_name, debt_amount in new_debtors.items():
            DbHelper.session.add(Debtor(full_name=full_name, debt_amount=debt_amount))

        DbHelper.session.commit()

    @staticmethod
    def get_debt_by_name(full_name: str) -> float:
        logger.debug(f"Получение долга для пользователя {full_name}")

        debtor = DbHelper.session.query(Debtor).filter(Debtor.full_name == full_name).first()

        if debtor is None:
            return 0

        return float(debtor.debt_amount)

    @staticmethod
    def get_all_debtors():
        logger.debug("Получение списка всех должников")

        debtors_list = DbHelper.session.query(Debtor).all()

        return debtors_list
