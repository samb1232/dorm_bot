import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, patch, AsyncMock, call
from states_functions.registration_functions import (
    get_name,
    get_room_number,
    choose_corpus,
    no_command
)
from enums.enumerations import ConversationStates


@pytest.fixture
def mock_update():
    """Create a mock Update object"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    update.message = Mock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock Context object"""
    context = Mock()
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    return context


class TestGetName:
    """Test suite for get_name function"""

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.DbHelper.set_user_full_name')
    async def test_get_name_valid_full_name(self, mock_set_name, mock_update, mock_context):
        """Test getting a valid full name with both first and last name"""
        # Arrange
        mock_update.message.text = "Иван Иванов"

        # Act
        result = await get_name(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_ROOM_NUMBER
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Иванов" in call_args
        mock_set_name.assert_called_once_with(12345, "иван иванов")

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.DbHelper.set_user_full_name')
    async def test_get_name_with_middle_name(self, mock_set_name, mock_update, mock_context):
        """Test getting full name with middle name"""
        # Arrange
        mock_update.message.text = "Петров Петр Петрович"

        # Act
        result = await get_name(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_ROOM_NUMBER
        mock_set_name.assert_called_once_with(12345, "петров петр петрович")

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.DbHelper.set_user_full_name')
    async def test_get_name_with_yo_character(self, mock_set_name, mock_update, mock_context):
        """Test that 'ё' is replaced with 'е' in the name"""
        # Arrange
        mock_update.message.text = "Фёдоров Алёна"

        # Act
        result = await get_name(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_ROOM_NUMBER
        mock_set_name.assert_called_once_with(12345, "федоров алена")

    @pytest.mark.asyncio
    async def test_get_name_single_word(self, mock_update, mock_context):
        """Test getting name with only one word (invalid)"""
        # Arrange
        mock_update.message.text = "Иван"

        # Act
        result = await get_name(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once_with(
            "У тебя должно быть как минимум Имя и Фамилия"
        )

    @pytest.mark.asyncio
    async def test_get_name_empty_string(self, mock_update, mock_context):
        """Test getting an empty name"""
        # Arrange
        mock_update.message.text = ""

        # Act
        result = await get_name(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()


class TestGetRoomNumber:
    """Test suite for get_room_number function"""

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.DbHelper.set_user_room')
    async def test_get_room_number_valid(self, mock_set_room, mock_update, mock_context):
        """Test getting a valid room number"""
        # Arrange
        mock_update.message.text = "305"

        # Act
        result = await get_room_number(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_CORPUS
        mock_set_room.assert_called_once_with(12345, 305)
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "305" in call_args

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.DbHelper.set_user_room')
    async def test_get_room_number_zero(self, mock_set_room, mock_update, mock_context):
        """Test getting room number 0"""
        # Arrange
        mock_update.message.text = "0"

        # Act
        result = await get_room_number(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_CORPUS
        mock_set_room.assert_called_once_with(12345, 0)

    @pytest.mark.asyncio
    async def test_get_room_number_invalid_text(self, mock_update, mock_context):
        """Test getting invalid room number (text)"""
        # Arrange
        mock_update.message.text = "триста пятая"

        # Act
        result = await get_room_number(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once_with(
            "Я тебя не понял. Введи номер комнаты коректно"
        )

    @pytest.mark.asyncio
    async def test_get_room_number_invalid_mixed(self, mock_update, mock_context):
        """Test getting mixed numbers and text"""
        # Arrange
        mock_update.message.text = "305A"

        # Act
        result = await get_room_number(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()


class TestChooseCorpus:
    """Test suite for choose_corpus function"""

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.menu_functions.main_menu')
    @patch('states_functions.registration_functions.DbHelper.set_user_lives_in_b')
    async def test_choose_corpus_a(self, mock_set_lives_in_b, mock_main_menu, mock_update, mock_context):
        """Test choosing corpus A"""
        # Arrange
        mock_update.message.text = "а"
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await choose_corpus(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_set_lives_in_b.assert_called_once_with(12345, False)
        mock_update.message.reply_text.assert_called_once_with("Отлично! Регистрация закончена.")
        mock_main_menu.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.menu_functions.main_menu')
    @patch('states_functions.registration_functions.DbHelper.set_user_lives_in_b')
    async def test_choose_corpus_b(self, mock_set_lives_in_b, mock_main_menu, mock_update, mock_context):
        """Test choosing corpus B"""
        # Arrange
        mock_update.message.text = "б"
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await choose_corpus(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_set_lives_in_b.assert_called_once_with(12345, True)
        mock_main_menu.assert_called_once()

    @pytest.mark.asyncio
    @patch('states_functions.registration_functions.menu_functions.main_menu')
    @patch('states_functions.registration_functions.DbHelper.set_user_lives_in_b')
    async def test_choose_corpus_uppercase(self, mock_set_lives_in_b, mock_main_menu, mock_update, mock_context):
        """Test choosing corpus with uppercase letters"""
        # Arrange
        mock_update.message.text = "А"
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await choose_corpus(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_set_lives_in_b.assert_called_once_with(12345, False)

    @pytest.mark.asyncio
    async def test_choose_corpus_invalid(self, mock_update, mock_context):
        """Test choosing invalid corpus"""
        # Arrange
        mock_update.message.text = "С"

        # Act
        result = await choose_corpus(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once_with(
            "Я тебя не понял. Введи корпус корректно (А или Б)"
        )

    @pytest.mark.asyncio
    async def test_choose_corpus_number(self, mock_update, mock_context):
        """Test entering a number instead of corpus letter"""
        # Arrange
        mock_update.message.text = "5"

        # Act
        result = await choose_corpus(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()


class TestNoCommand:
    """Test suite for no_command function"""

    @pytest.mark.asyncio
    async def test_no_command(self, mock_update, mock_context):
        """Test no_command function"""
        # Act
        result = await no_command(mock_update, mock_context)

        # Assert
        assert result is None
        mock_context.bot.send_message.assert_called_once_with(
            text="Не командуй мне тут. Делай что говорят",
            chat_id=12345
        )
