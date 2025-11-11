import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telegram.error import TelegramError

import bot_instance
from configs.my_logger import get_logger
import strings
from database.db_operations import DbHelper
from google_api.google_sheets_api import GoogleSheetsAPI


logger = get_logger(__name__)

scheduler = None


def setup_scheduler() -> AsyncIOScheduler:
    global scheduler

    if scheduler is not None:
        logger.warning("Планировщик уже инициализирован")
        return scheduler

    logger.info("Инициализация планировщика задач")
    scheduler = AsyncIOScheduler()

    # Синхронизация должников из Google Sheets каждые 12 часов
    scheduler.add_job(
        batch_debtors_async,
        trigger=IntervalTrigger(hours=12),
        id='batch_debtors',
        name='Синхронизация должников из Google Sheets',
        replace_existing=True
    )

    # Отправка уведомлений должникам в 10:00 в дни 1, 5, 10, 13
    scheduler.add_job(
        send_notifications_to_all_debtors,
        trigger=CronTrigger(hour=10, minute=0, day='1,5,10,13'),
        id='send_notifications',
        name='Рассылка уведомлений должникам',
        replace_existing=True
    )

    logger.info("Планировщик настроен успешно")
    return scheduler


async def batch_debtors_async():
    try:
        logger.info("Начало синхронизации должников из Google Sheets")
        await asyncio.to_thread(GoogleSheetsAPI.batch_debtors_from_sheets)
        logger.info("Синхронизация должников завершена успешно")
    except Exception as e:
        logger.error(f"Ошибка при синхронизации должников: {e}", exc_info=True)


async def send_notifications_to_all_debtors():
    today = datetime.datetime.now()

    if today.day not in [1, 5, 10, 13]:
        logger.info(f"Пропуск рассылки: сегодня {today.day} число")
        return

    try:
        logger.info("Начало рассылки уведомлений должникам")

        debtors_list = await asyncio.to_thread(DbHelper.get_all_debtors)

        if not debtors_list:
            logger.info("Список должников пуст, рассылка не требуется")
            return

        logger.info(f"Найдено должников: {len(debtors_list)}")

        # Создаем задачи для параллельной отправки с ограничением
        semaphore = asyncio.Semaphore(10)  # Максимум 10 одновременных отправок
        tasks = [
            send_notification_to_debtor(debtor, semaphore)
            for debtor in debtors_list
        ]

        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        error_count = sum(1 for r in results if isinstance(r, Exception) or r is False)

        logger.info(
            f"Рассылка завершена. Успешно: {success_count}, "
            f"Ошибок: {error_count}, Всего: {len(debtors_list)}"
        )

    except Exception as e:
        logger.error(f"Критическая ошибка при рассылке уведомлений: {e}", exc_info=True)


async def send_notification_to_debtor(debtor, semaphore: asyncio.Semaphore) -> bool:
    async with semaphore:
        try:
            user_id = await asyncio.to_thread(
                DbHelper.get_user_id_by_full_name,
                debtor.full_name
            )

            if user_id is None:
                logger.warning(
                    f"Пользователь не найден в БД: {debtor.full_name}, "
                    f"долг: {debtor.debt_amount}"
                )
                return False

            message_text = (
                f"{strings.DEBT_NOTIFICATION_TEXT[0]}"
                f"{debtor.debt_amount}"
                f"{strings.DEBT_NOTIFICATION_TEXT[1]}"
            )

            await bot_instance.bot.send_message(
                text=message_text,
                chat_id=user_id
            )

            logger.debug(
                f"Уведомление отправлено: {debtor.full_name} "
                f"(user_id: {user_id}, долг: {debtor.debt_amount})"
            )
            return True

        except TelegramError as e:
            logger.warning(
                f"Telegram ошибка при отправке уведомления {debtor.full_name}: {e}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при отправке уведомления {debtor.full_name}: {e}",
                exc_info=True
            )
            return False
