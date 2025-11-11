import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
from unittest.mock import Mock, patch, AsyncMock
import pytest

from notifications.notifications import (
    setup_scheduler,
    batch_debtors_async,
    send_notifications_to_all_debtors,
    send_notification_to_debtor
)
from database.tables.debtors_table import Debtor
from telegram.error import TelegramError


class TestSetupScheduler:
    """Test suite for scheduler setup"""

    def test_setup_scheduler_creates_new_instance(self):
        """Test that setup_scheduler creates a new scheduler instance"""
        # Arrange
        import notifications.notifications as notifications_module
        notifications_module.scheduler = None

        # Act
        scheduler = setup_scheduler()

        # Assert
        assert scheduler is not None
        assert notifications_module.scheduler is not None
        assert scheduler == notifications_module.scheduler

    def test_setup_scheduler_returns_existing_instance(self):
        """Test that setup_scheduler returns existing scheduler if already initialized"""
        # Arrange
        import notifications.notifications as notifications_module
        first_scheduler = setup_scheduler()

        # Act
        second_scheduler = setup_scheduler()

        # Assert
        assert first_scheduler == second_scheduler
        assert notifications_module.scheduler == first_scheduler

    @patch('notifications.notifications.logger')
    def test_setup_scheduler_configures_jobs(self, mock_logger):
        """Test that setup_scheduler properly configures scheduled jobs"""
        # Arrange
        import notifications.notifications as notifications_module
        notifications_module.scheduler = None

        # Act
        scheduler = setup_scheduler()

        # Assert
        jobs = scheduler.get_jobs()
        assert len(jobs) == 2

        # Check that batch_debtors job exists
        batch_job = scheduler.get_job('batch_debtors')
        assert batch_job is not None
        assert batch_job.name == 'Синхронизация должников из Google Sheets'

        # Check that send_notifications job exists
        notifications_job = scheduler.get_job('send_notifications')
        assert notifications_job is not None
        assert notifications_job.name == 'Рассылка уведомлений должникам'


class TestBatchDebtorsAsync:
    """Test suite for batch_debtors_async function"""

    @pytest.mark.asyncio
    @patch('notifications.notifications.GoogleSheetsAPI.batch_debtors_from_sheets')
    @patch('notifications.notifications.logger')
    async def test_batch_debtors_async_success(self, mock_logger, mock_batch_debtors):
        """Test successful execution of batch_debtors_async"""
        # Arrange
        mock_batch_debtors.return_value = None

        # Act
        await batch_debtors_async()

        # Assert
        mock_batch_debtors.assert_called_once()
        mock_logger.info.assert_any_call("Начало синхронизации должников из Google Sheets")
        mock_logger.info.assert_any_call("Синхронизация должников завершена успешно")
        mock_logger.error.assert_not_called()

    @pytest.mark.asyncio
    @patch('notifications.notifications.GoogleSheetsAPI.batch_debtors_from_sheets')
    @patch('notifications.notifications.logger')
    async def test_batch_debtors_async_handles_exception(self, mock_logger, mock_batch_debtors):
        """Test that batch_debtors_async handles exceptions properly"""
        # Arrange
        mock_batch_debtors.side_effect = Exception("Google Sheets API error")

        # Act
        await batch_debtors_async()

        # Assert
        mock_batch_debtors.assert_called_once()
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args
        assert "Ошибка при синхронизации должников" in error_call_args[0][0]


class TestSendNotificationsToAllDebtors:
    """Test suite for send_notifications_to_all_debtors function"""

    @pytest.mark.asyncio
    @patch('notifications.notifications.datetime')
    async def test_send_notifications_wrong_day(self, mock_datetime):
        """Test that notifications are not sent on wrong days"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 15  # Not a notification day
        mock_datetime.datetime.now.return_value = mock_now

        # Act
        await send_notifications_to_all_debtors()

        # Assert - function should return early, no further processing

    @pytest.mark.asyncio
    @patch('notifications.notifications.DbHelper.get_all_debtors')
    @patch('notifications.notifications.datetime')
    @patch('notifications.notifications.logger')
    async def test_send_notifications_empty_debtors_list(self, mock_logger, mock_datetime, mock_get_debtors):
        """Test handling of empty debtors list"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 1  # Notification day
        mock_datetime.datetime.now.return_value = mock_now
        mock_get_debtors.return_value = []

        # Act
        await send_notifications_to_all_debtors()

        # Assert
        mock_logger.info.assert_any_call("Список должников пуст, рассылка не требуется")

    @pytest.mark.asyncio
    @patch('notifications.notifications.send_notification_to_debtor')
    @patch('notifications.notifications.DbHelper.get_all_debtors')
    @patch('notifications.notifications.datetime')
    @patch('notifications.notifications.logger')
    async def test_send_notifications_success(self, mock_logger, mock_datetime, mock_get_debtors, mock_send_notification):
        """Test successful sending of notifications to all debtors"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 5  # Notification day
        mock_datetime.datetime.now.return_value = mock_now

        mock_debtors = [
            Debtor(full_name="иван иванов", debt_amount=1500.50),
            Debtor(full_name="петр петров", debt_amount=2000.0),
            Debtor(full_name="мария сидорова", debt_amount=750.25)
        ]
        mock_get_debtors.return_value = mock_debtors

        # Mock send_notification_to_debtor to return True (success)
        mock_send_notification.return_value = True

        # Act
        await send_notifications_to_all_debtors()

        # Assert
        assert mock_send_notification.call_count == 3
        mock_logger.info.assert_any_call("Найдено должников: 3")
        mock_logger.info.assert_any_call(
            "Рассылка завершена. Успешно: 3, Ошибок: 0, Всего: 3"
        )

    @pytest.mark.asyncio
    @patch('notifications.notifications.send_notification_to_debtor')
    @patch('notifications.notifications.DbHelper.get_all_debtors')
    @patch('notifications.notifications.datetime')
    @patch('notifications.notifications.logger')
    async def test_send_notifications_partial_failure(self, mock_logger, mock_datetime, mock_get_debtors, mock_send_notification):
        """Test notifications with partial failures"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 10  # Notification day
        mock_datetime.datetime.now.return_value = mock_now

        mock_debtors = [
            Debtor(full_name="успешный пользователь", debt_amount=1000.0),
            Debtor(full_name="неудачный пользователь", debt_amount=2000.0),
            Debtor(full_name="еще успешный", debt_amount=500.0)
        ]
        mock_get_debtors.return_value = mock_debtors

        # First and third succeed, second fails
        mock_send_notification.side_effect = [True, False, True]

        # Act
        await send_notifications_to_all_debtors()

        # Assert
        assert mock_send_notification.call_count == 3
        mock_logger.info.assert_any_call(
            "Рассылка завершена. Успешно: 2, Ошибок: 1, Всего: 3"
        )

    @pytest.mark.asyncio
    @patch('notifications.notifications.DbHelper.get_all_debtors')
    @patch('notifications.notifications.datetime')
    @patch('notifications.notifications.logger')
    async def test_send_notifications_handles_exception(self, mock_logger, mock_datetime, mock_get_debtors):
        """Test that send_notifications handles exceptions properly"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 13  # Notification day
        mock_datetime.datetime.now.return_value = mock_now

        mock_get_debtors.side_effect = Exception("Database error")

        # Act
        await send_notifications_to_all_debtors()

        # Assert
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args
        assert "Критическая ошибка при рассылке уведомлений" in error_call_args[0][0]


class TestSendNotificationToDebtor:
    """Test suite for send_notification_to_debtor function"""

    @pytest.mark.asyncio
    @patch('notifications.notifications.bot_instance')
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.strings.DEBT_NOTIFICATION_TEXT', ['Ваш долг составляет ', ' рублей'])
    async def test_send_notification_success(self, mock_get_user_id, mock_bot_instance):
        """Test successful notification sending"""
        # Arrange
        debtor = Debtor(full_name="иван иванов", debt_amount=1500.50)
        semaphore = asyncio.Semaphore(10)
        mock_get_user_id.return_value = 12345

        # Mock bot's send_message method
        mock_send_message = AsyncMock(return_value=None)
        mock_bot_instance.bot.send_message = mock_send_message

        # Act
        result = await send_notification_to_debtor(debtor, semaphore)

        # Assert
        assert result is True
        mock_get_user_id.assert_called_once_with("иван иванов")
        mock_send_message.assert_called_once()
        call_kwargs = mock_send_message.call_args[1]
        assert call_kwargs['chat_id'] == 12345
        assert '1500.5' in call_kwargs['text']

    @pytest.mark.asyncio
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.logger')
    async def test_send_notification_user_not_found(self, mock_logger, mock_get_user_id):
        """Test handling when user is not found in database"""
        # Arrange
        debtor = Debtor(full_name="несуществующий пользователь", debt_amount=1000.0)
        semaphore = asyncio.Semaphore(10)
        mock_get_user_id.return_value = None

        # Act
        result = await send_notification_to_debtor(debtor, semaphore)

        # Assert
        assert result is False
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "Пользователь не найден в БД" in warning_message
        assert "несуществующий пользователь" in warning_message

    @pytest.mark.asyncio
    @patch('notifications.notifications.bot_instance')
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.logger')
    @patch('notifications.notifications.strings.DEBT_NOTIFICATION_TEXT', ['Долг: ', ' руб'])
    async def test_send_notification_telegram_error(self, mock_logger, mock_get_user_id, mock_bot_instance):
        """Test handling of Telegram errors"""
        # Arrange
        debtor = Debtor(full_name="петр петров", debt_amount=2000.0)
        semaphore = asyncio.Semaphore(10)
        mock_get_user_id.return_value = 54321

        # Mock bot's send_message method to raise TelegramError
        mock_send_message = AsyncMock(side_effect=TelegramError("Bot was blocked by the user"))
        mock_bot_instance.bot.send_message = mock_send_message

        # Act
        result = await send_notification_to_debtor(debtor, semaphore)

        # Assert
        assert result is False
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "Telegram ошибка" in warning_message
        assert "петр петров" in warning_message

    @pytest.mark.asyncio
    @patch('notifications.notifications.bot_instance')
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.logger')
    @patch('notifications.notifications.strings.DEBT_NOTIFICATION_TEXT', ['Долг: ', ' руб'])
    async def test_send_notification_unexpected_error(self, mock_logger, mock_get_user_id, mock_bot_instance):
        """Test handling of unexpected errors"""
        # Arrange
        debtor = Debtor(full_name="мария сидорова", debt_amount=750.25)
        semaphore = asyncio.Semaphore(10)
        mock_get_user_id.return_value = 99999

        # Mock bot's send_message method to raise Exception
        mock_send_message = AsyncMock(side_effect=Exception("Unexpected error"))
        mock_bot_instance.bot.send_message = mock_send_message

        # Act
        result = await send_notification_to_debtor(debtor, semaphore)

        # Assert
        assert result is False
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Неожиданная ошибка" in error_message
        assert "мария сидорова" in error_message

    @pytest.mark.asyncio
    @patch('notifications.notifications.bot_instance')
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.strings.DEBT_NOTIFICATION_TEXT', ['Долг: ', ' руб'])
    async def test_send_notification_respects_semaphore(self, mock_get_user_id, mock_bot_instance):
        """Test that semaphore properly limits concurrent executions"""
        # Arrange
        debtors = [
            Debtor(full_name=f"пользователь {i}", debt_amount=1000.0 + i)
            for i in range(20)
        ]
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent
        mock_get_user_id.return_value = 12345

        # Track concurrent execution count
        concurrent_count = 0
        max_concurrent = 0

        async def mock_send_with_delay(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.01)  # Simulate network delay
            concurrent_count -= 1

        # Mock bot's send_message method
        mock_send_message = AsyncMock(side_effect=mock_send_with_delay)
        mock_bot_instance.bot.send_message = mock_send_message

        # Act
        tasks = [
            send_notification_to_debtor(debtor, semaphore)
            for debtor in debtors
        ]
        results = await asyncio.gather(*tasks)

        # Assert
        assert all(results)  # All should succeed
        assert max_concurrent <= 5  # Should never exceed semaphore limit


class TestNotificationsIntegration:
    """Integration tests for notifications module"""

    @pytest.mark.asyncio
    @patch('notifications.notifications.bot_instance')
    @patch('notifications.notifications.DbHelper.get_user_id_by_full_name')
    @patch('notifications.notifications.DbHelper.get_all_debtors')
    @patch('notifications.notifications.datetime')
    @patch('notifications.notifications.strings.DEBT_NOTIFICATION_TEXT', ['Долг: ', ' руб'])
    async def test_full_notification_flow(self, mock_datetime, mock_get_all_debtors,
                                         mock_get_user_id, mock_bot_instance):
        """Test complete notification flow from getting debtors to sending messages"""
        # Arrange
        mock_now = Mock()
        mock_now.day = 1
        mock_datetime.datetime.now.return_value = mock_now

        mock_debtors = [
            Debtor(full_name="пользователь 1", debt_amount=1000.0),
            Debtor(full_name="пользователь 2", debt_amount=2000.0)
        ]
        mock_get_all_debtors.return_value = mock_debtors
        mock_get_user_id.side_effect = [111, 222]

        # Mock bot's send_message method
        mock_send_message = AsyncMock(return_value=None)
        mock_bot_instance.bot.send_message = mock_send_message

        # Act
        await send_notifications_to_all_debtors()

        # Assert
        assert mock_send_message.call_count == 2
        assert mock_get_user_id.call_count == 2

        # Verify message content and recipients
        calls = mock_send_message.call_args_list
        assert calls[0][1]['chat_id'] == 111
        assert '1000.0' in calls[0][1]['text']
        assert calls[1][1]['chat_id'] == 222
        assert '2000.0' in calls[1][1]['text']
