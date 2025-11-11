import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, patch, AsyncMock
from states_functions.menu_functions import (
    start,
    main_menu,
    callback_buttons_manager,
    info,
    send_info,
    unknown_callback_handler,
    show_profile
)
from enums.enumerations import ConversationStates, MenuCallbackButtons, ChangeProfileCallbackButtons
from database.tables.users_table import User


@pytest.fixture
def mock_update():
    """Create a mock Update object"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_user.name = "TestUser"
    update.effective_chat.id = 12345
    update.callback_query = Mock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.message = Mock()
    update.callback_query.message.edit_reply_markup = AsyncMock()
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


class TestStart:
    """Test suite for start function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.add_new_user')
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_start_new_user(self, mock_strings, mock_get_user, mock_add_user,
                                  mock_update, mock_context):
        """Test start with a new user (registration)"""
        # Arrange
        mock_get_user.return_value = None
        mock_strings.GREETING_TEXT = "Привет!"

        # Act
        result = await start(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.REGISTRATION_FULL_NAME
        mock_get_user.assert_called_once_with(12345)
        mock_add_user.assert_called_once_with(user_id=12345)
        mock_context.bot.send_message.assert_called_once_with(
            text="Привет!",
            chat_id=12345
        )

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.main_menu')
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    async def test_start_existing_user(self, mock_get_user, mock_main_menu,
                                      mock_update, mock_context, mock_user):
        """Test start with existing user (goes to main menu)"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await start(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_get_user.assert_called_once_with(12345)
        mock_main_menu.assert_called_once_with(mock_update, mock_context)


class TestMainMenu:
    """Test suite for main_menu function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.strings')
    async def test_main_menu(self, mock_strings, mock_update, mock_context):
        """Test main menu display"""
        # Arrange
        mock_strings.MAIN_MENU_TEXT = "Главное меню"
        mock_strings.INFO_TEXT = "Информация"
        mock_strings.PAYMENT_BUTTON_TEXT = "Оплата"
        mock_strings.PROFILE_BUTTON_TEXT = "Профиль"

        # Act
        result = await main_menu(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert call_args[1]['text'] == "Главное меню"
        assert call_args[1]['chat_id'] == 12345
        assert call_args[1]['reply_markup'] is not None


class TestInfo:
    """Test suite for info function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.strings')
    async def test_info(self, mock_strings, mock_update, mock_context):
        """Test info menu display"""
        # Arrange
        mock_strings.INFO_TEXT = "Информация"
        mock_strings.KOMENDANT_BUTTON_TEXT = "Комендант"
        mock_strings.KASTELANSHA_BUTTON_TEXT = "Кастелянша"
        mock_strings.SHOWER_BUTTON_TEXT = "Душевые"
        mock_strings.LAUNDARY_BUTTON_TEXT = "Прачечная"
        mock_strings.GUESTS_BUTTON_TEXT = "Гости"
        mock_strings.GYM_BUTTON_TEXT = "Спортзал"
        mock_strings.STUDY_ROOM_BUTTON_TEXT = "Учебная комната"
        mock_strings.MANSARDA_BUTTON_TEXT = "Мансарда"
        mock_strings.STUDSOVET_BUTTON_TEXT = "Студсовет"
        mock_strings.MAIN_MENU_BUTTON_TEXT = "Главное меню"

        # Act
        result = await info(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert call_args[1]['text'] == "Информация"
        assert call_args[1]['reply_markup'] is not None


class TestSendInfo:
    """Test suite for send_info function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_send_info_komendant(self, mock_strings, mock_get_user,
                                      mock_update, mock_context, mock_user):
        """Test sending komendant info"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_strings.KOMENDANT_INFO_TEXT = "Информация о коменданте"

        # Act
        result = await send_info(mock_update, mock_context, MenuCallbackButtons.KOMENDANT_INFO)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_context.bot.send_message.assert_called_once_with(
            text="Информация о коменданте",
            chat_id=12345
        )

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_send_info_studsovet_corpus_a(self, mock_strings, mock_get_user,
                                                mock_update, mock_context, mock_user):
        """Test sending studsovet info for corpus A"""
        # Arrange
        mock_user.lives_in_b = False
        mock_get_user.return_value = mock_user
        mock_strings.STUDSOVET_INFO_A_TEXT = "Студсовет корпус А"

        # Act
        result = await send_info(mock_update, mock_context, MenuCallbackButtons.STUDSOVET_INFO)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_context.bot.send_message.assert_called_once_with(
            text="Студсовет корпус А",
            chat_id=12345
        )

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_send_info_studsovet_corpus_b(self, mock_strings, mock_get_user,
                                                mock_update, mock_context, mock_user):
        """Test sending studsovet info for corpus B"""
        # Arrange
        mock_user.lives_in_b = True
        mock_get_user.return_value = mock_user
        mock_strings.STUDSOVET_INFO_B_TEXT = "Студсовет корпус Б"

        # Act
        result = await send_info(mock_update, mock_context, MenuCallbackButtons.STUDSOVET_INFO)

        # Assert
        mock_context.bot.send_message.assert_called_once_with(
            text="Студсовет корпус Б",
            chat_id=12345
        )

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_send_info_shower(self, mock_strings, mock_get_user,
                                   mock_update, mock_context, mock_user):
        """Test sending shower info"""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_strings.SHOWER_INFO_TEXT = "Информация о душевых"

        # Act
        result = await send_info(mock_update, mock_context, MenuCallbackButtons.SHOWER_INFO)

        # Assert
        mock_context.bot.send_message.assert_called_once_with(
            text="Информация о душевых",
            chat_id=12345
        )


class TestShowProfile:
    """Test suite for show_profile function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_show_profile_corpus_a(self, mock_strings, mock_get_user,
                                        mock_update, mock_context, mock_user):
        """Test showing profile for corpus A user"""
        # Arrange
        mock_user.lives_in_b = False
        mock_get_user.return_value = mock_user
        mock_strings.CHANGE_NAME_BUTTON_TEXT = "Изменить имя"
        mock_strings.CHANGE_ROOM_BUTTON_TEXT = "Изменить комнату"
        mock_strings.CHANGE_CORPUS_BUTTON_TEXT = "Изменить корпус"
        mock_strings.MAIN_MENU_BUTTON_TEXT = "Главное меню"

        # Act
        result = await show_profile(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_get_user.assert_called_once_with(12345)
        mock_context.bot.send_message.assert_called_once()

        call_args = mock_context.bot.send_message.call_args
        info_text = call_args[1]['text']
        assert "Иван Иванов" in info_text
        assert "305" in info_text
        assert "Корпус: А" in info_text

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.DbHelper.get_user_by_id')
    @patch('states_functions.menu_functions.strings')
    async def test_show_profile_corpus_b(self, mock_strings, mock_get_user,
                                        mock_update, mock_context, mock_user):
        """Test showing profile for corpus B user"""
        # Arrange
        mock_user.lives_in_b = True
        mock_get_user.return_value = mock_user
        mock_strings.CHANGE_NAME_BUTTON_TEXT = "Изменить имя"
        mock_strings.CHANGE_ROOM_BUTTON_TEXT = "Изменить комнату"
        mock_strings.CHANGE_CORPUS_BUTTON_TEXT = "Изменить корпус"
        mock_strings.MAIN_MENU_BUTTON_TEXT = "Главное меню"

        # Act
        result = await show_profile(mock_update, mock_context)

        # Assert
        call_args = mock_context.bot.send_message.call_args
        info_text = call_args[1]['text']
        assert "Корпус: Б" in info_text


class TestUnknownCallbackHandler:
    """Test suite for unknown_callback_handler function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.start')
    async def test_unknown_callback_handler(self, mock_start, mock_update, mock_context):
        """Test unknown callback handler"""
        # Arrange
        mock_start.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await unknown_callback_handler(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_update.callback_query.message.edit_reply_markup.assert_called_once_with(None)
        mock_update.callback_query.answer.assert_called_once()
        mock_start.assert_called_once_with(mock_update, mock_context)


class TestCallbackButtonsManager:
    """Test suite for callback_buttons_manager function"""

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.info')
    async def test_callback_manager_info(self, mock_info, mock_update, mock_context):
        """Test callback manager routing to info"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.INFO
        mock_info.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        assert result == ConversationStates.MAIN_MENU
        mock_update.callback_query.answer.assert_called_once()
        mock_info.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.main_menu')
    async def test_callback_manager_main_menu(self, mock_main_menu, mock_update, mock_context):
        """Test callback manager routing to main menu"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.MAIN_MENU
        mock_main_menu.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_main_menu.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.payment_functions.payment_info')
    async def test_callback_manager_payment(self, mock_payment_info, mock_update, mock_context):
        """Test callback manager routing to payment"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.PAYMENT
        mock_payment_info.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_payment_info.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.payment_functions.send_check')
    async def test_callback_manager_send_check(self, mock_send_check, mock_update, mock_context):
        """Test callback manager routing to send check"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.SEND_CHECK
        mock_send_check.return_value = ConversationStates.PAYMENT

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_send_check.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.show_profile')
    async def test_callback_manager_profile(self, mock_show_profile, mock_update, mock_context):
        """Test callback manager routing to profile"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.PROFILE
        mock_show_profile.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_show_profile.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.change_profile_functions.change_user_full_name')
    async def test_callback_manager_change_name(self, mock_change_name, mock_update, mock_context):
        """Test callback manager routing to change name"""
        # Arrange
        mock_update.callback_query.data = ChangeProfileCallbackButtons.CHANGE_NAME
        mock_change_name.return_value = ConversationStates.CHANGE_FULL_NAME

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_change_name.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.change_profile_functions.change_user_room_number')
    async def test_callback_manager_change_room(self, mock_change_room, mock_update, mock_context):
        """Test callback manager routing to change room"""
        # Arrange
        mock_update.callback_query.data = ChangeProfileCallbackButtons.CHANGE_ROOM
        mock_change_room.return_value = ConversationStates.CHANGE_ROOM_NUMBER

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_change_room.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.change_profile_functions.change_user_corpus')
    async def test_callback_manager_change_corpus(self, mock_change_corpus, mock_update, mock_context):
        """Test callback manager routing to change corpus"""
        # Arrange
        mock_update.callback_query.data = ChangeProfileCallbackButtons.CHANGE_CORPUS
        mock_change_corpus.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_change_corpus.assert_called_once_with(mock_update, mock_context)

    @pytest.mark.asyncio
    @patch('states_functions.menu_functions.send_info')
    async def test_callback_manager_komendant_info(self, mock_send_info, mock_update, mock_context):
        """Test callback manager routing to komendant info"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.KOMENDANT_INFO
        mock_send_info.return_value = ConversationStates.MAIN_MENU

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        mock_send_info.assert_called_once_with(
            mock_update,
            mock_context,
            MenuCallbackButtons.KOMENDANT_INFO
        )

    @pytest.mark.asyncio
    async def test_callback_manager_question(self, mock_update, mock_context):
        """Test callback manager for question feature (in development)"""
        # Arrange
        mock_update.callback_query.data = MenuCallbackButtons.QUESTION

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        assert result is None
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "в разработке" in call_args[1]['text']

    @pytest.mark.asyncio
    async def test_callback_manager_unknown_callback(self, mock_update, mock_context):
        """Test callback manager with unknown callback data"""
        # Arrange
        mock_update.callback_query.data = "UNKNOWN_CALLBACK"

        # Act
        result = await callback_buttons_manager(mock_update, mock_context)

        # Assert
        assert result is None
        mock_update.callback_query.answer.assert_called_once()
