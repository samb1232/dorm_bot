import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from unittest.mock import Mock, patch, MagicMock
from database.db_operations import DbHelper
from database.tables.users_table import User
from database.tables.debtors_table import Debtor


class TestDbHelperUserOperations:
    """Test suite for user-related database operations"""

    @patch('database.db_operations.DbHelper.session')
    def test_get_user_by_id_found(self, mock_session):
        """Test getting a user by ID when user exists"""
        # Arrange
        expected_user = User(user_id=123, full_name="Test User", lives_in_b=True, room_number=101)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = expected_user

        # Act
        result = DbHelper.get_user_by_id(123)

        # Assert
        assert result == expected_user
        mock_session.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()

    @patch('database.db_operations.DbHelper.session')
    def test_get_user_by_id_not_found(self, mock_session):
        """Test getting a user by ID when user doesn't exist"""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None

        # Act
        result = DbHelper.get_user_by_id(999)

        # Assert
        assert result is None

    @patch('database.db_operations.DbHelper.session')
    def test_get_user_id_by_full_name_found(self, mock_session):
        """Test getting user ID by full name when user exists"""
        # Arrange
        mock_user = User(user_id=456, full_name="Иван Иванов", lives_in_b=False, room_number=202)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_user

        # Act
        result = DbHelper.get_user_id_by_full_name("Иван Иванов")

        # Assert
        assert result == 456
        mock_session.query.assert_called_once_with(User)

    @patch('database.db_operations.DbHelper.session')
    def test_get_user_id_by_full_name_not_found(self, mock_session):
        """Test getting user ID by full name when user doesn't exist"""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None

        # Act
        result = DbHelper.get_user_id_by_full_name("Несуществующий Пользователь")

        # Assert
        assert result is None

    @patch('database.db_operations.DbHelper.session')
    def test_add_new_user(self, mock_session):
        """Test adding a new user to the database"""
        # Arrange
        user_id = 789
        full_name = "Петр Петров"
        lives_in_b = True
        room_number = 303

        # Act
        DbHelper.add_new_user(user_id, full_name, lives_in_b, room_number)

        # Assert
        mock_session.add.assert_called_once()
        added_user = mock_session.add.call_args[0][0]
        assert isinstance(added_user, User)
        assert added_user.user_id == user_id
        assert added_user.full_name == full_name
        assert added_user.lives_in_b == lives_in_b
        assert added_user.room_number == room_number
        mock_session.commit.assert_called_once()

    @patch('database.db_operations.DbHelper.session')
    def test_add_new_user_with_defaults(self, mock_session):
        """Test adding a new user with default values"""
        # Arrange
        user_id = 100

        # Act
        DbHelper.add_new_user(user_id)

        # Assert
        added_user = mock_session.add.call_args[0][0]
        assert added_user.user_id == user_id
        assert added_user.full_name == ""
        assert added_user.lives_in_b is False
        assert added_user.room_number == -1

    @patch('database.db_operations.DbHelper.get_user_by_id')
    @patch('database.db_operations.DbHelper.session')
    def test_set_user_full_name(self, mock_session, mock_get_user):
        """Test setting user's full name"""
        # Arrange
        mock_user = User(user_id=123, full_name="Old Name", lives_in_b=True, room_number=101)
        mock_get_user.return_value = mock_user
        new_name = "New Name"

        # Act
        DbHelper.set_user_full_name(123, new_name)

        # Assert
        assert mock_user.full_name == new_name
        mock_session.commit.assert_called_once()

    @patch('database.db_operations.DbHelper.get_user_by_id')
    @patch('database.db_operations.DbHelper.session')
    def test_set_user_lives_in_b(self, mock_session, mock_get_user):
        """Test setting user's dormitory building status"""
        # Arrange
        mock_user = User(user_id=123, full_name="Test User", lives_in_b=False, room_number=101)
        mock_get_user.return_value = mock_user

        # Act
        DbHelper.set_user_lives_in_b(123, True)

        # Assert
        assert mock_user.lives_in_b is True
        mock_session.commit.assert_called_once()

    @patch('database.db_operations.DbHelper.get_user_by_id')
    @patch('database.db_operations.DbHelper.session')
    def test_set_user_room(self, mock_session, mock_get_user):
        """Test setting user's room number"""
        # Arrange
        mock_user = User(user_id=123, full_name="Test User", lives_in_b=True, room_number=101)
        mock_get_user.return_value = mock_user
        new_room = 202

        # Act
        DbHelper.set_user_room(123, new_room)

        # Assert
        assert mock_user.room_number == new_room
        mock_session.commit.assert_called_once()


class TestDbHelperDebtorOperations:
    """Test suite for debtor-related database operations"""

    @patch('database.db_operations.DbHelper.session')
    def test_update_debtors_table(self, mock_session):
        """Test updating the debtors table with new data"""
        # Arrange
        new_debtors = {
            "иван иванов": 1500.50,
            "петр петров": 2000.00,
            "мария сидорова": 750.25
        }
        mock_query = Mock()
        mock_session.query.return_value = mock_query

        # Act
        DbHelper.update_debtors_table(new_debtors)

        # Assert
        # Verify old debtors were deleted
        mock_session.query.assert_called_with(Debtor)
        mock_query.delete.assert_called_once()

        # Verify new debtors were added
        assert mock_session.add.call_count == 3

        # Check that commit was called
        mock_session.commit.assert_called_once()

    @patch('database.db_operations.DbHelper.session')
    def test_update_debtors_table_empty(self, mock_session):
        """Test updating debtors table with empty dictionary"""
        # Arrange
        new_debtors = {}
        mock_query = Mock()
        mock_session.query.return_value = mock_query

        # Act
        DbHelper.update_debtors_table(new_debtors)

        # Assert
        mock_query.delete.assert_called_once()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()

    @patch('database.db_operations.DbHelper.session')
    def test_get_debt_by_name_found(self, mock_session):
        """Test getting debt amount by name when debtor exists"""
        # Arrange
        mock_debtor = Debtor(full_name="иван иванов", debt_amount=1500.50)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_debtor

        # Act
        result = DbHelper.get_debt_by_name("иван иванов")

        # Assert
        assert result == 1500.50
        mock_session.query.assert_called_once_with(Debtor)

    @patch('database.db_operations.DbHelper.session')
    def test_get_debt_by_name_not_found(self, mock_session):
        """Test getting debt amount when debtor doesn't exist"""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None

        # Act
        result = DbHelper.get_debt_by_name("несуществующий должник")

        # Assert
        assert result == 0

    @patch('database.db_operations.DbHelper.session')
    def test_get_debt_by_name_zero_debt(self, mock_session):
        """Test getting debt amount when debt is zero"""
        # Arrange
        mock_debtor = Debtor(full_name="петр петров", debt_amount=0.0)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_debtor

        # Act
        result = DbHelper.get_debt_by_name("петр петров")

        # Assert
        assert result == 0.0

    @patch('database.db_operations.DbHelper.session')
    def test_get_all_debtors(self, mock_session):
        """Test getting all debtors from the database"""
        # Arrange
        mock_debtors = [
            Debtor(full_name="иван иванов", debt_amount=1500.50),
            Debtor(full_name="петр петров", debt_amount=2000.00),
            Debtor(full_name="мария сидорова", debt_amount=750.25)
        ]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = mock_debtors

        # Act
        result = DbHelper.get_all_debtors()

        # Assert
        assert len(result) == 3
        assert result == mock_debtors
        mock_session.query.assert_called_once_with(Debtor)

    @patch('database.db_operations.DbHelper.session')
    def test_get_all_debtors_empty(self, mock_session):
        """Test getting all debtors when table is empty"""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = DbHelper.get_all_debtors()

        # Assert
        assert result == []
