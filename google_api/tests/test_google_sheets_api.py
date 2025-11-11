import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from unittest.mock import Mock, patch, MagicMock
from google_api.google_sheets_api import GoogleSheetsAPI
from oauth2client.service_account import ServiceAccountCredentials


class TestGoogleSheetsAPIAuthentication:
    """Test suite for GoogleSheetsAPI authentication"""

    @patch('google_api.google_sheets_api.Config.get_google_credentials')
    @patch('google_api.google_sheets_api.ServiceAccountCredentials.from_json_keyfile_dict')
    def test_authenticate_success(self, mock_from_json, mock_get_credentials):
        """Test successful authentication"""
        # Arrange
        mock_credentials_dict = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key': 'test-key',
            'client_email': 'test@test.com'
        }
        mock_get_credentials.return_value = mock_credentials_dict
        mock_creds = Mock(spec=ServiceAccountCredentials)
        mock_from_json.return_value = mock_creds

        # Act
        result = GoogleSheetsAPI._authenticate()

        # Assert
        assert result == mock_creds
        mock_get_credentials.assert_called_once()
        mock_from_json.assert_called_once_with(
            mock_credentials_dict,
            GoogleSheetsAPI.SCOPES
        )

    @patch('google_api.google_sheets_api.Config.get_google_credentials')
    @patch('google_api.google_sheets_api.logger')
    def test_authenticate_failure(self, mock_logger, mock_get_credentials):
        """Test authentication failure when credentials are invalid"""
        # Arrange
        mock_get_credentials.side_effect = Exception("Credential error")

        # Act
        result = GoogleSheetsAPI._authenticate()

        # Assert
        assert result is None
        mock_logger.error.assert_called_once()


class TestGoogleSheetsAPIGetDebtorsTable:
    """Test suite for getting debtors table from Google Sheets"""

    @patch('google_api.google_sheets_api.GoogleSheetsAPI._authenticate')
    @patch('google_api.google_sheets_api.apiclient.discovery.build')
    @patch('google_api.google_sheets_api.httplib2.Http')
    @patch('google_api.google_sheets_api.Config')
    def test_get_debtors_table_success(self, mock_config, mock_http, mock_build, mock_authenticate):
        """Test successfully retrieving debtors from both sheets"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds
        mock_creds.authorize.return_value = Mock()

        # Mock the Google Sheets service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock spreadsheet values responses
        mock_values_a = {
            'values': [
                ['Иванов Иван', '1500.50'],
                ['Петров Петр', '2000'],
                ['', ''],  # Empty row should be skipped
                ['Сидорова Мария', '750,25'],
                ['Incomplete'],  # Row with only one element should be skipped
            ]
        }

        mock_values_b = {
            'values': [
                ['Козлов Андрей', '3000.00'],
                ['Смирнова Ёлена', '1250'],  # Test 'ё' replacement
            ]
        }

        mock_spreadsheet = Mock()
        mock_values_method = Mock()
        mock_get_method = Mock()

        mock_service.spreadsheets.return_value = mock_spreadsheet
        mock_spreadsheet.values.return_value = mock_values_method
        mock_values_method.get.return_value = mock_get_method

        # Configure different return values for two consecutive calls
        mock_get_method.execute.side_effect = [mock_values_a, mock_values_b]

        # Act
        result = GoogleSheetsAPI.get_debtors_table()

        # Assert
        assert len(result) == 5
        assert result['иванов иван'] == 1500.50
        assert result['петров петр'] == 2000.0
        assert result['сидорова мария'] == 750.25
        assert result['козлов андрей'] == 3000.0
        assert result['смирнова елена'] == 1250.0  # 'ё' replaced with 'е'

        # Verify API calls
        assert mock_values_method.get.call_count == 2
        assert mock_get_method.execute.call_count == 2

    @patch('google_api.google_sheets_api.GoogleSheetsAPI._authenticate')
    @patch('google_api.google_sheets_api.apiclient.discovery.build')
    @patch('google_api.google_sheets_api.httplib2.Http')
    @patch('google_api.google_sheets_api.Config')
    def test_get_debtors_table_with_special_characters(self, mock_config, mock_http, mock_build, mock_authenticate):
        """Test debt amount parsing with various special characters"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds
        mock_creds.authorize.return_value = Mock()

        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock values with special characters in debt amounts
        mock_values_a = {
            'values': [
                ['Тест Один', '1500,50руб'],  # Comma separator and text
                ['Тест Два', '-250.00'],  # Negative amount
                ['Тест Три', '3.14руб'],  # Dot separator and text
            ]
        }

        mock_values_b = {
            'values': []
        }

        mock_spreadsheet = Mock()
        mock_values_method = Mock()
        mock_get_method = Mock()

        mock_service.spreadsheets.return_value = mock_spreadsheet
        mock_spreadsheet.values.return_value = mock_values_method
        mock_values_method.get.return_value = mock_get_method
        mock_get_method.execute.side_effect = [mock_values_a, mock_values_b]

        # Act
        result = GoogleSheetsAPI.get_debtors_table()

        # Assert
        assert result['тест один'] == 1500.50
        assert result['тест два'] == -250.00
        assert result['тест три'] == 3.14

    @patch('google_api.google_sheets_api.GoogleSheetsAPI._authenticate')
    @patch('google_api.google_sheets_api.apiclient.discovery.build')
    @patch('google_api.google_sheets_api.httplib2.Http')
    @patch('google_api.google_sheets_api.Config')
    def test_get_debtors_table_empty_sheets(self, mock_config, mock_http, mock_build, mock_authenticate):
        """Test retrieving from empty sheets"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds
        mock_creds.authorize.return_value = Mock()

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_values_a = {'values': []}
        mock_values_b = {'values': []}

        mock_spreadsheet = Mock()
        mock_values_method = Mock()
        mock_get_method = Mock()

        mock_service.spreadsheets.return_value = mock_spreadsheet
        mock_spreadsheet.values.return_value = mock_values_method
        mock_values_method.get.return_value = mock_get_method
        mock_get_method.execute.side_effect = [mock_values_a, mock_values_b]

        # Act
        result = GoogleSheetsAPI.get_debtors_table()

        # Assert
        assert result == {}

    @patch('google_api.google_sheets_api.GoogleSheetsAPI._authenticate')
    @patch('google_api.google_sheets_api.apiclient.discovery.build')
    @patch('google_api.google_sheets_api.httplib2.Http')
    @patch('google_api.google_sheets_api.Config')
    def test_get_debtors_table_filters_invalid_rows(self, mock_config, mock_http, mock_build, mock_authenticate):
        """Test that invalid rows are properly filtered"""
        # Arrange
        mock_config.GS_SPREADSHEETS_ID = 'test-spreadsheet-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds
        mock_creds.authorize.return_value = Mock()

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_values_a = {
            'values': [
                ['Valid Name', '1000'],  # Valid
                ['Name Only'],  # Invalid - only one column
                ['', '500'],  # Invalid - empty name
                ['Name', ''],  # Invalid - empty debt
                ['Valid Name 2', '2000'],  # Valid
                [],  # Invalid - completely empty
            ]
        }

        mock_values_b = {'values': []}

        mock_spreadsheet = Mock()
        mock_values_method = Mock()
        mock_get_method = Mock()

        mock_service.spreadsheets.return_value = mock_spreadsheet
        mock_spreadsheet.values.return_value = mock_values_method
        mock_values_method.get.return_value = mock_get_method
        mock_get_method.execute.side_effect = [mock_values_a, mock_values_b]

        # Act
        result = GoogleSheetsAPI.get_debtors_table()

        # Assert
        assert len(result) == 2
        assert result['valid name'] == 1000.0
        assert result['valid name 2'] == 2000.0


class TestGoogleSheetsAPIBatchDebtors:
    """Test suite for batch debtor operations"""

    @patch('google_api.google_sheets_api.DbHelper.update_debtors_table')
    @patch('google_api.google_sheets_api.GoogleSheetsAPI.get_debtors_table')
    def test_batch_debtors_from_sheets_success(self, mock_get_debtors, mock_update_debtors):
        """Test successfully batching debtors from sheets to database"""
        # Arrange
        mock_debtors = {
            'иванов иван': 1500.50,
            'петров петр': 2000.0
        }
        mock_get_debtors.return_value = mock_debtors

        # Act
        GoogleSheetsAPI.batch_debtors_from_sheets()

        # Assert
        mock_get_debtors.assert_called_once()
        mock_update_debtors.assert_called_once_with(mock_debtors)

    @patch('google_api.google_sheets_api.DbHelper.update_debtors_table')
    @patch('google_api.google_sheets_api.GoogleSheetsAPI.get_debtors_table')
    def test_batch_debtors_from_sheets_empty(self, mock_get_debtors, mock_update_debtors):
        """Test batching when no debtors are found"""
        # Arrange
        mock_get_debtors.return_value = {}

        # Act
        GoogleSheetsAPI.batch_debtors_from_sheets()

        # Assert
        mock_get_debtors.assert_called_once()
        mock_update_debtors.assert_called_once_with({})


class TestGoogleSheetsAPIConstants:
    """Test suite for GoogleSheetsAPI constants"""

    def test_scopes_defined(self):
        """Test that SCOPES is properly defined"""
        assert GoogleSheetsAPI.SCOPES == ['https://www.googleapis.com/auth/spreadsheets']

    def test_list_names_defined(self):
        """Test that list names are properly defined"""
        assert GoogleSheetsAPI.LIST_A == "ДОЛГ 5а"
        assert GoogleSheetsAPI.LIST_B == "ДОЛГ 5б"

    def test_range_defined(self):
        """Test that range is properly defined"""
        assert GoogleSheetsAPI.RANGE == "A2:C500"
