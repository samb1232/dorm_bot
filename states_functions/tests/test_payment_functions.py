import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from states_functions.payment_functions import (
    payment_info,
    send_check,
    unknown_message_handler,
    cancel_sending_check,
    receive_check_file
)
from enums.enumerations import ConversationStates
from database.tables.users_table import User


@pytest.fixture
def mock_update():
    """Create a mock Update object"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    update.message = Mock()
    update.callback_query = Mock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock Context object"""
    context = Mock()
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    context.bot.get_file = AsyncMock()
    return context


@pytest.fixture
def mock_user():
    """Create a mock User object"""
    return User(
        user_id=12345,
        full_name="иван иванов",
        lives_in_b=False,
        room_number=305
    )


class TestPaymentInfo:
    """Test suite for payment_info function"""

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.DbHelper.get_debt_by_name')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    @patch('states_functions.payment_functions.Config')
    async def test_payment_info_with_debt(self, mock_config, mock_get_user,
                                         mock_get_debt, mock_update, mock_context, mock_user):
        """Test payment info when user has debt"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'
        mock_get_user.return_value = mock_user
        mock_get_debt.return_value = 1500.50

        # Act
        result = await payment_info(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_get_user.assert_called_once_with(12345)
        mock_get_debt.assert_called_once_with("иван иванов")

        # Verify message was sent
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "1500.5 руб" in call_args[1]['text']
        assert call_args[1]['chat_id'] == 12345

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.DbHelper.get_debt_by_name')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    @patch('states_functions.payment_functions.Config')
    async def test_payment_info_no_debt(self, mock_config, mock_get_user,
                                       mock_get_debt, mock_update, mock_context, mock_user):
        """Test payment info when user has no debt"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'
        mock_get_user.return_value = mock_user
        mock_get_debt.return_value = 0

        # Act
        result = await payment_info(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        call_args = mock_context.bot.send_message.call_args
        assert "нет долга" in call_args[1]['text']

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.DbHelper.get_debt_by_name')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    @patch('states_functions.payment_functions.Config')
    async def test_payment_info_keyboard_buttons(self, mock_config, mock_get_user,
                                                 mock_get_debt, mock_update, mock_context, mock_user):
        """Test that payment info includes correct keyboard buttons"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'
        mock_get_user.return_value = mock_user
        mock_get_debt.return_value = 0

        # Act
        result = await payment_info(mock_update, mock_context)

        # Assert
        call_args = mock_context.bot.send_message.call_args
        reply_markup = call_args[1]['reply_markup']
        assert reply_markup is not None


class TestSendCheck:
    """Test suite for send_check function"""

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    async def test_send_check(self, mock_strings, mock_update, mock_context):
        """Test send_check function"""
        # Arrange
        mock_strings.SEND_CHECK_TEXT = "Отправьте чек"

        # Act
        result = await send_check(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.PAYMENT
        mock_context.bot.send_message.assert_called_once_with(
            text="Отправьте чек",
            chat_id=12345
        )


class TestUnknownMessageHandler:
    """Test suite for unknown_message_handler function"""

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    async def test_unknown_message_handler(self, mock_strings, mock_update, mock_context):
        """Test unknown message handler"""
        # Arrange
        mock_strings.UNKNOWN_TEXT = "Неизвестная команда"

        # Act
        await unknown_message_handler(mock_update, mock_context)

        # Assert
        mock_context.bot.send_message.assert_called_once_with(
            text="Неизвестная команда",
            chat_id=12345
        )


class TestCancelSendingCheck:
    """Test suite for cancel_sending_check function"""

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.menu_functions.main_menu')
    @patch('states_functions.payment_functions.strings')
    async def test_cancel_sending_check(self, mock_strings, mock_main_menu,
                                       mock_update, mock_context):
        """Test canceling check sending"""
        # Arrange
        mock_strings.CANCEL_TEXT = "Отменено"
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await cancel_sending_check(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_context.bot.send_message.assert_called_once_with(
            text="Отменено",
            chat_id=12345
        )
        mock_main_menu.assert_called_once_with(mock_update, mock_context)


class TestReceiveCheckFile:
    """Test suite for receive_check_file function"""

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.menu_functions.main_menu')
    @patch('states_functions.payment_functions.os.remove')
    @patch('states_functions.payment_functions.GoogleDriveAPI.upload_file')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_document_pdf(self, mock_get_user, mock_upload,
                                              mock_remove, mock_main_menu,
                                              mock_update, mock_context, mock_user):
        """Test receiving a PDF document as check"""
        # Arrange
        mock_user.lives_in_b = False
        mock_get_user.return_value = mock_user
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        mock_document = Mock()
        mock_document.file_id = "file123"
        mock_document.file_name = "check.pdf"
        mock_document.file_unique_id = "unique123"
        mock_update.message.document = mock_document
        mock_update.message.photo = []
        mock_update.message.sticker = None
        mock_update.message.voice = None

        mock_file = Mock()
        mock_file.download_to_drive = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file
        mock_upload.return_value = "uploaded-file-id"

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_get_user.assert_called_once_with(12345)
        mock_context.bot.get_file.assert_called_once_with("file123")

        # Verify file was downloaded with correct name
        download_call = mock_file.download_to_drive.call_args[0][0]
        assert download_call.startswith("5А_иван_иванов_unique123.pdf")

        mock_upload.assert_called_once()
        mock_remove.assert_called_once()

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.menu_functions.main_menu')
    @patch('states_functions.payment_functions.os.remove')
    @patch('states_functions.payment_functions.GoogleDriveAPI.upload_file')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_document_corpus_b(self, mock_get_user, mock_upload,
                                                   mock_remove, mock_main_menu,
                                                   mock_update, mock_context, mock_user):
        """Test receiving check from corpus B"""
        # Arrange
        mock_user.lives_in_b = True
        mock_get_user.return_value = mock_user
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        mock_document = Mock()
        mock_document.file_id = "file123"
        mock_document.file_name = "check.pdf"
        mock_document.file_unique_id = "unique123"
        mock_update.message.document = mock_document
        mock_update.message.photo = []
        mock_update.message.sticker = None
        mock_update.message.voice = None

        mock_file = Mock()
        mock_file.download_to_drive = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        download_call = mock_file.download_to_drive.call_args[0][0]
        assert download_call.startswith("5Б_")

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.menu_functions.main_menu')
    @patch('states_functions.payment_functions.os.remove')
    @patch('states_functions.payment_functions.GoogleDriveAPI.upload_file')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_photo(self, mock_get_user, mock_upload,
                                      mock_remove, mock_main_menu,
                                      mock_update, mock_context, mock_user):
        """Test receiving a photo as check"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        mock_photo = Mock()
        mock_photo.file_id = "photo123"
        mock_photo.file_unique_id = "unique456"
        mock_update.message.document = None
        mock_update.message.photo = [mock_photo]
        mock_update.message.sticker = None
        mock_update.message.voice = None

        mock_file = Mock()
        mock_file.download_to_drive = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        download_call = mock_file.download_to_drive.call_args[0][0]
        assert download_call.endswith(".png")

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_sticker(self, mock_get_user, mock_strings,
                                        mock_update, mock_context, mock_user):
        """Test receiving a sticker (invalid)"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_update.message.document = None
        mock_update.message.photo = []
        mock_update.message.sticker = Mock()
        mock_update.message.voice = None

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.PAYMENT
        mock_context.bot.send_message.assert_called_once()
        assert "*посмеялся*" in mock_context.bot.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_voice(self, mock_get_user, mock_strings,
                                      mock_update, mock_context, mock_user):
        """Test receiving a voice message (invalid)"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_update.message.document = None
        mock_update.message.photo = []
        mock_update.message.sticker = None
        mock_update.message.voice = Mock()

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.PAYMENT
        mock_context.bot.send_message.assert_called_once()
        assert "тебя не слышно" in mock_context.bot.send_message.call_args[1]['text']

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_invalid_extension(self, mock_get_user, mock_strings,
                                                   mock_update, mock_context, mock_user):
        """Test receiving file with invalid extension"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_strings.INCORRECT_FILE_TEXT = "Неверный тип файла"

        mock_document = Mock()
        mock_document.file_id = "file123"
        mock_document.file_name = "check.txt"
        mock_document.file_unique_id = "unique123"
        mock_update.message.document = mock_document
        mock_update.message.photo = []
        mock_update.message.sticker = None
        mock_update.message.voice = None

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.PAYMENT
        mock_context.bot.send_message.assert_called_once_with(
            text="Неверный тип файла",
            chat_id=12345
        )

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_valid_extensions(self, mock_get_user, mock_strings,
                                                  mock_update, mock_context, mock_user):
        """Test that all valid extensions are accepted"""
        # Arrange
        mock_get_user.return_value = mock_user
        valid_extensions = ["jpg", "jpeg", "png", "pdf"]

        for ext in valid_extensions:
            mock_update.message.document = Mock()
            mock_update.message.document.file_id = "file123"
            mock_update.message.document.file_name = f"check.{ext}"
            mock_update.message.document.file_unique_id = "unique123"
            mock_update.message.photo = []
            mock_update.message.sticker = None
            mock_update.message.voice = None

            mock_file = Mock()
            mock_file.download_to_drive = AsyncMock()
            mock_context.bot.get_file.return_value = mock_file

            with patch('states_functions.payment_functions.GoogleDriveAPI.upload_file'):
                with patch('states_functions.payment_functions.os.remove'):
                    with patch('states_functions.payment_functions.menu_functions.main_menu') as mock_menu:
                        mock_menu.return_value = ConversationStates.MAIN_MENU

                        # Act
                        result = await receive_check_file(mock_update, mock_context)

                        # Assert
                        assert result == ConversationStates.MAIN_MENU

    @pytest.mark.asyncio
    @patch('states_functions.payment_functions.strings')
    @patch('states_functions.payment_functions.DbHelper.get_user_by_id')
    async def test_receive_check_no_valid_message_type(self, mock_get_user, mock_strings,
                                                       mock_update, mock_context, mock_user):
        """Test receiving message with no valid type"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_strings.INCORRECT_FILE_TEXT = "Неверный тип файла"

        mock_update.message.document = None
        mock_update.message.photo = []
        mock_update.message.sticker = None
        mock_update.message.voice = None

        # Act
        result = await receive_check_file(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.PAYMENT
        mock_context.bot.send_message.assert_called_once_with(
            text="Неверный тип файла",
            chat_id=12345
        )
