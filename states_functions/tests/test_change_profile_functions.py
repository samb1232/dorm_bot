import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, patch, AsyncMock
from states_functions.change_profile_functions import (
    change_user_corpus,
    change_user_full_name,
    change_user_room_number,
    full_name_change_handler,
    room_number_change_handler
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
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock Context object"""
    context = Mock()
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
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


class TestChangeUserCorpus:
    """Test suite for change_user_corpus function"""

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_lives_in_b')
    @patch('states_functions.change_profile_functions.DbHelper.get_user_by_id')
    @patch('states_functions.change_profile_functions.strings')
    async def test_change_corpus_from_a_to_b(self, mock_strings, mock_get_user,
                                            mock_set_lives_in_b, mock_show_profile,
                                            mock_update, mock_context, mock_user):
        """Test changing corpus from A to B"""
        # Arrange
        mock_user.lives_in_b = False
        mock_get_user.return_value = mock_user
        mock_strings.CORPUS_CHANGED_TEXT = "Корпус изменен"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await change_user_corpus(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_get_user.assert_called_once_with(12345)
        mock_set_lives_in_b.assert_called_once_with(12345, True)
        mock_context.bot.send_message.assert_called_once_with(
            text="Корпус изменен",
            chat_id=12345
        )
        mock_show_profile.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_lives_in_b')
    @patch('states_functions.change_profile_functions.DbHelper.get_user_by_id')
    @patch('states_functions.change_profile_functions.strings')
    async def test_change_corpus_from_b_to_a(self, mock_strings, mock_get_user,
                                            mock_set_lives_in_b, mock_show_profile,
                                            mock_update, mock_context, mock_user):
        """Test changing corpus from B to A"""
        # Arrange
        mock_user.lives_in_b = True
        mock_get_user.return_value = mock_user
        mock_strings.CORPUS_CHANGED_TEXT = "Корпус изменен"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await change_user_corpus(mock_update, mock_context)

        # Assert
        mock_set_lives_in_b.assert_called_once_with(12345, False)


class TestChangeUserFullName:
    """Test suite for change_user_full_name function"""

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.strings')
    async def test_change_user_full_name(self, mock_strings, mock_update, mock_context):
        """Test initiating full name change"""
        # Arrange
        mock_strings.ENTER_FULL_NAME_TEXT = "Введите полное имя"

        # Act
        result = await change_user_full_name(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.CHANGE_FULL_NAME
        mock_context.bot.send_message.assert_called_once_with(
            text="Введите полное имя",
            chat_id=12345
        )


class TestChangeUserRoomNumber:
    """Test suite for change_user_room_number function"""

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.strings')
    async def test_change_user_room_number(self, mock_strings, mock_update, mock_context):
        """Test initiating room number change"""
        # Arrange
        mock_strings.ENTER_ROOM_NUMBER_TEXT = "Введите номер комнаты"

        # Act
        result = await change_user_room_number(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.CHANGE_ROOM_NUMBER
        mock_context.bot.send_message.assert_called_once_with(
            text="Введите номер комнаты",
            chat_id=12345
        )


class TestFullNameChangeHandler:
    """Test suite for full_name_change_handler function"""

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_full_name')
    @patch('states_functions.change_profile_functions.strings')
    async def test_full_name_change_valid(self, mock_strings, mock_set_name,
                                         mock_show_profile, mock_update, mock_context):
        """Test changing full name with valid input"""
        # Arrange
        mock_update.message.text = "Петров Петр"
        mock_strings.FULL_NAME_CHANGED_TEXT = "ФИО изменено"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await full_name_change_handler(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_set_name.assert_called_once_with(12345, "петров петр")
        mock_update.message.reply_text.assert_called_once_with("ФИО изменено")
        mock_show_profile.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_full_name')
    @patch('states_functions.change_profile_functions.strings')
    async def test_full_name_change_with_yo(self, mock_strings, mock_set_name,
                                           mock_show_profile, mock_update, mock_context):
        """Test changing full name with 'ё' character"""
        # Arrange
        mock_update.message.text = "Фёдоров Алёна"
        mock_strings.FULL_NAME_CHANGED_TEXT = "ФИО изменено"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await full_name_change_handler(mock_update, mock_context)

        # Assert
        mock_set_name.assert_called_once_with(12345, "федоров алена")

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_full_name')
    @patch('states_functions.change_profile_functions.strings')
    async def test_full_name_change_with_middle_name(self, mock_strings, mock_set_name,
                                                     mock_show_profile, mock_update, mock_context):
        """Test changing full name with middle name"""
        # Arrange
        mock_update.message.text = "Иванов Иван Иванович"
        mock_strings.FULL_NAME_CHANGED_TEXT = "ФИО изменено"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await full_name_change_handler(mock_update, mock_context)

        # Assert
        mock_set_name.assert_called_once_with(12345, "иванов иван иванович")

    @pytest.mark.asyncio
    async def test_full_name_change_single_word(self, mock_update, mock_context):
        """Test changing full name with only one word (invalid)"""
        # Arrange
        mock_update.message.text = "Иван"

        # Act
        result = await full_name_change_handler(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once_with(
            "У тебя должно быть как минимум фамилия и имя"
        )

    @pytest.mark.asyncio
    async def test_full_name_change_empty(self, mock_update, mock_context):
        """Test changing full name with empty string"""
        # Arrange
        mock_update.message.text = ""

        # Act
        result = await full_name_change_handler(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()


class TestRoomNumberChangeHandler:
    """Test suite for room_number_change_handler function"""

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_room')
    @patch('states_functions.change_profile_functions.strings')
    async def test_room_number_change_valid(self, mock_strings, mock_set_room,
                                           mock_show_profile, mock_update, mock_context):
        """Test changing room number with valid input"""
        # Arrange
        mock_update.message.text = "404"
        mock_strings.ROOM_NUMBER_CHANGED_TEXT = "Номер комнаты изменен"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await room_number_change_handler(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_set_room.assert_called_once_with(12345, 404)
        mock_update.message.reply_text.assert_called_once_with("Номер комнаты изменен")
        mock_show_profile.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.change_profile_functions.menu_functions.show_profile')
    @patch('states_functions.change_profile_functions.DbHelper.set_user_room')
    @patch('states_functions.change_profile_functions.strings')
    async def test_room_number_change_zero(self, mock_strings, mock_set_room,
                                          mock_show_profile, mock_update, mock_context):
        """Test changing room number to 0"""
        # Arrange
        mock_update.message.text = "0"
        mock_strings.ROOM_NUMBER_CHANGED_TEXT = "Номер комнаты изменен"
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await room_number_change_handler(mock_update, mock_context)

        # Assert
        mock_set_room.assert_called_once_with(12345, 0)

    @pytest.mark.asyncio
    async def test_room_number_change_invalid_text(self, mock_update, mock_context):
        """Test changing room number with text (invalid)"""
        # Arrange
        mock_update.message.text = "триста пятая"

        # Act
        result = await room_number_change_handler(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once_with(
            "Я тебя не понял. Введи номер комнаты корректно"
        )

    @pytest.mark.asyncio
    async def test_room_number_change_invalid_mixed(self, mock_update, mock_context):
        """Test changing room number with mixed text and numbers"""
        # Arrange
        mock_update.message.text = "305A"

        # Act
        result = await room_number_change_handler(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_room_number_change_negative(self, mock_update, mock_context):
        """Test changing room number with negative number"""
        # Arrange
        mock_update.message.text = "-5"

        # Act
        result = await room_number_change_handler(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.message.reply_text.assert_called_once()
