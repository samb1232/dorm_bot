import asyncio
import datetime

import aioschedule
import schedule

import bot_instance
from configs.my_logger import get_logger
import strings
from database.db_operations import DbHelper
from google_api.google_sheets_api import GoogleSheetsAPI


logger = get_logger(__name__)


def start_schedule_functions():
    GoogleSheetsAPI.batch_debtors_from_sheets()
    schedule.every(12).hours.do(GoogleSheetsAPI.batch_debtors_from_sheets)
    aioschedule.every().day.at("10:00").do(send_notifications_to_all_debtors)


async def run_schedules():
    while True:
        schedule.run_pending()
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def send_notifications_to_all_debtors():
    today = datetime.datetime.now()
    if today.day not in [1, 5, 10, 13]:
        return

    debtors_list = DbHelper.get_all_debtors()
    for debtor in debtors_list:
        user_id = DbHelper.get_user_id_by_full_name(debtor.full_name)
        if user_id is None:
            continue

        try:
            await bot_instance.bot.send_message(
                text=f"{strings.DEBT_NOTIFICATION_TEXT[0]}{debtor.debt_amount}{strings.DEBT_NOTIFICATION_TEXT[1]}",
                chat_id=user_id
            )
        except Exception as e:
            logger.warning(e)
