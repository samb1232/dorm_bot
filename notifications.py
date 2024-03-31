import asyncio
import datetime
import time

import schedule

import bot_instance
from database.db_operations import DbHelper
from google_sheets_api import GoogleSheetsAPI


def start_schedule_functions():
    GoogleSheetsAPI.batch_debtors_from_sheets()
    schedule.every(12).hours.do(GoogleSheetsAPI.batch_debtors_from_sheets)

    # schedule.every().day.at("17:02").do(send_notifications_to_all_debtors)
    # schedule.every(30).seconds.do(send_notifications_to_all_debtors)


def run_schedules():
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_notifications_to_all_debtors():
    today = datetime.datetime.now()
    if today.day not in [1, 5, 10, 15, 31]:
        return

    debtors_list = DbHelper.get_all_debtors()
    for debtor in debtors_list:
        user_id = DbHelper.get_user_id_by_full_name(debtor.full_name)
        if user_id is None:
            continue

        asyncio.run(bot_instance.bot.send_message(
            text=f"Твой долг по оплате общежития составляет {debtor.debt_amount} руб. "
                 f"Можешь оплатить его через главное меню, нажав на кнопку 'Оплата за общежитие'",
            chat_id=user_id))
