import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from unittest.mock import Mock, patch, MagicMock
import pytest
from google_api.google_drive_api import GoogleDriveAPI
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


class TestGoogleDriveAPIAuthentication:
    """Test suite for GoogleDriveAPI authentication"""

    @patch('google_api.google_drive_api.Config.get_google_credentials')
    @patch('google_api.google_drive_api.service_account.Credentials.from_service_account_info')
    def test_authenticate_success(self, mock_from_service_account, mock_get_credentials):
        """Test successful authentication"""
        # Arrange
        mock_credentials_dict = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key': 'test-key',
            'client_email': 'test@test.com'
        }
        mock_get_credentials.return_value = mock_credentials_dict
        mock_creds = Mock(spec=service_account.Credentials)
        mock_from_service_account.return_value = mock_creds

        # Act
        result = GoogleDriveAPI._authenticate()

        # Assert
        assert result == mock_creds
        mock_get_credentials.assert_called_once()
        mock_from_service_account.assert_called_once_with(
            mock_credentials_dict,
            scopes=GoogleDriveAPI.SCOPES
        )

    @patch('google_api.google_drive_api.Config.get_google_credentials')
    @patch('google_api.google_drive_api.logger')
    def test_authenticate_no_credentials(self, mock_logger, mock_get_credentials):
        """Test authentication when credentials are not found"""
        # Arrange
        mock_get_credentials.return_value = None

        # Act
        result = GoogleDriveAPI._authenticate()

        # Assert
        assert result is None
        mock_logger.error.assert_called_once_with("Google credentials not found in configuration")

    @patch('google_api.google_drive_api.Config.get_google_credentials')
    @patch('google_api.google_drive_api.logger')
    def test_authenticate_failure(self, mock_logger, mock_get_credentials):
        """Test authentication failure with exception"""
        # Arrange
        mock_get_credentials.side_effect = Exception("Credential error")

        # Act
        result = GoogleDriveAPI._authenticate()

        # Assert
        assert result is None
        mock_logger.error.assert_called()


class TestGoogleDriveAPIUploadFile:
    """Test suite for file upload functionality"""

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.MediaFileUpload')
    @patch('google_api.google_drive_api.Config')
    def test_upload_file_success(self, mock_config, mock_media_upload, mock_build, mock_authenticate):
        """Test successfully uploading a file"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_create = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create
        mock_create.execute.return_value = {'id': 'uploaded-file-id'}

        file_path = '/path/to/test.pdf'
        file_name = 'test.pdf'

        # Act
        result = GoogleDriveAPI.upload_file(file_path, file_name)

        # Assert
        assert result == 'uploaded-file-id'
        mock_authenticate.assert_called_once()
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
        mock_media_upload.assert_called_once_with(
            file_path,
            mimetype='application/pdf',
            resumable=True
        )

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.logger')
    def test_upload_file_authentication_failure(self, mock_logger, mock_authenticate):
        """Test upload file when authentication fails"""
        # Arrange
        mock_authenticate.return_value = None

        # Act
        result = GoogleDriveAPI.upload_file('/path/to/file.pdf', 'file.pdf')

        # Assert
        assert result is False
        mock_logger.error.assert_called_with("Failed to authenticate, aborting upload.")

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.MediaFileUpload')
    @patch('google_api.google_drive_api.logger')
    @patch('google_api.google_drive_api.Config')
    def test_upload_file_http_error(self, mock_config, mock_logger, mock_media_upload, mock_build, mock_authenticate):
        """Test upload file when HTTP error occurs"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_create = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create

        # Create a proper HttpError
        http_error = HttpError(
            resp=Mock(status=403),
            content=b'Forbidden'
        )
        mock_create.execute.side_effect = http_error

        # Act
        result = GoogleDriveAPI.upload_file('/path/to/file.pdf', 'file.pdf')

        # Assert
        assert result is False
        mock_logger.error.assert_called()

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.MediaFileUpload')
    @patch('google_api.google_drive_api.logger')
    @patch('google_api.google_drive_api.Config')
    def test_upload_file_generic_exception(self, mock_config, mock_logger, mock_media_upload, mock_build, mock_authenticate):
        """Test upload file when generic exception occurs"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.side_effect = Exception("Unexpected error")

        # Act
        result = GoogleDriveAPI.upload_file('/path/to/file.pdf', 'file.pdf')

        # Assert
        assert result is False
        mock_logger.error.assert_called()


class TestGoogleDriveAPIGetMimeType:
    """Test suite for MIME type detection"""

    def test_get_mime_type_pdf(self):
        """Test MIME type for PDF files"""
        assert GoogleDriveAPI._get_mime_type('/path/to/file.pdf') == 'application/pdf'
        assert GoogleDriveAPI._get_mime_type('/path/to/file.PDF') == 'application/pdf'

    def test_get_mime_type_images(self):
        """Test MIME type for image files"""
        assert GoogleDriveAPI._get_mime_type('/path/to/image.jpg') == 'image/jpeg'
        assert GoogleDriveAPI._get_mime_type('/path/to/image.jpeg') == 'image/jpeg'
        assert GoogleDriveAPI._get_mime_type('/path/to/image.png') == 'image/png'
        assert GoogleDriveAPI._get_mime_type('/path/to/image.PNG') == 'image/png'

    def test_get_mime_type_documents(self):
        """Test MIME type for document files"""
        assert GoogleDriveAPI._get_mime_type('/path/to/doc.doc') == 'application/msword'
        assert GoogleDriveAPI._get_mime_type('/path/to/doc.docx') == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert GoogleDriveAPI._get_mime_type('/path/to/sheet.xls') == 'application/vnd.ms-excel'
        assert GoogleDriveAPI._get_mime_type('/path/to/sheet.xlsx') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def test_get_mime_type_archives(self):
        """Test MIME type for archive files"""
        assert GoogleDriveAPI._get_mime_type('/path/to/file.zip') == 'application/zip'
        assert GoogleDriveAPI._get_mime_type('/path/to/file.rar') == 'application/x-rar-compressed'

    def test_get_mime_type_text(self):
        """Test MIME type for text files"""
        assert GoogleDriveAPI._get_mime_type('/path/to/file.txt') == 'text/plain'

    def test_get_mime_type_unknown(self):
        """Test MIME type for unknown file extensions"""
        assert GoogleDriveAPI._get_mime_type('/path/to/file.unknown') == 'application/octet-stream'
        assert GoogleDriveAPI._get_mime_type('/path/to/file') == 'application/octet-stream'


class TestGoogleDriveAPICreateFolder:
    """Test suite for folder creation functionality"""

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_create_folder_success(self, mock_config, mock_build, mock_authenticate):
        """Test successfully creating a folder"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_create = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create
        mock_create.execute.return_value = {'id': 'new-folder-id'}

        folder_name = 'Test Folder'

        # Act
        result = GoogleDriveAPI.create_folder(folder_name)

        # Assert
        assert result == 'new-folder-id'
        mock_authenticate.assert_called_once()
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)

        # Verify create was called with correct parameters
        mock_files.create.assert_called_once()
        call_kwargs = mock_files.create.call_args[1]
        assert call_kwargs['body']['name'] == folder_name
        assert call_kwargs['body']['mimeType'] == 'application/vnd.google-apps.folder'
        assert 'parents' in call_kwargs['body']

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_create_folder_with_custom_parent(self, mock_config, mock_build, mock_authenticate):
        """Test creating a folder with custom parent folder ID"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'default-parent-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_create = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create
        mock_create.execute.return_value = {'id': 'new-folder-id'}

        folder_name = 'Test Folder'
        custom_parent_id = 'custom-parent-id'

        # Act
        result = GoogleDriveAPI.create_folder(folder_name, custom_parent_id)

        # Assert
        assert result == 'new-folder-id'

        # Verify the custom parent was used
        call_args = mock_files.create.call_args
        assert call_args[1]['body']['parents'] == ['custom-parent-id']

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.logger')
    def test_create_folder_authentication_failure(self, mock_logger, mock_authenticate):
        """Test folder creation when authentication fails"""
        # Arrange
        mock_authenticate.return_value = None

        # Act
        result = GoogleDriveAPI.create_folder('Test Folder')

        # Assert
        assert result is None
        mock_logger.error.assert_called_with("Failed to authenticate, aborting folder creation.")

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.logger')
    @patch('google_api.google_drive_api.Config')
    def test_create_folder_http_error(self, mock_config, mock_logger, mock_build, mock_authenticate):
        """Test folder creation when HTTP error occurs"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_create = Mock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create

        http_error = HttpError(
            resp=Mock(status=404),
            content=b'Parent folder not found'
        )
        mock_create.execute.side_effect = http_error

        # Act
        result = GoogleDriveAPI.create_folder('Test Folder')

        # Assert
        assert result is None
        mock_logger.error.assert_called()


class TestGoogleDriveAPIListFiles:
    """Test suite for listing files functionality"""

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_list_files_success(self, mock_config, mock_build, mock_authenticate):
        """Test successfully listing files in a folder"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files_list = [
            {'id': 'file1', 'name': 'test1.pdf', 'mimeType': 'application/pdf'},
            {'id': 'file2', 'name': 'test2.jpg', 'mimeType': 'image/jpeg'}
        ]

        mock_files = Mock()
        mock_list = Mock()
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list
        mock_list.execute.return_value = {'files': mock_files_list}

        # Act
        result = GoogleDriveAPI.list_files()

        # Assert
        assert result == mock_files_list
        assert len(result) == 2
        mock_authenticate.assert_called_once()
        mock_build.assert_called_once()

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_list_files_with_custom_folder(self, mock_config, mock_build, mock_authenticate):
        """Test listing files in a custom folder"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'default-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_list = Mock()
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list
        mock_list.execute.return_value = {'files': []}

        custom_folder_id = 'custom-folder-id'

        # Act
        result = GoogleDriveAPI.list_files(folder_id=custom_folder_id)

        # Assert
        # Verify the query used the custom folder ID
        call_args = mock_files.list.call_args
        assert custom_folder_id in call_args[1]['q']

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_list_files_with_query(self, mock_config, mock_build, mock_authenticate):
        """Test listing files with a custom query"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_list = Mock()
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list
        mock_list.execute.return_value = {'files': []}

        custom_query = "name contains 'test'"

        # Act
        result = GoogleDriveAPI.list_files(query=custom_query)

        # Assert
        call_args = mock_files.list.call_args
        assert custom_query in call_args[1]['q']

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.logger')
    def test_list_files_authentication_failure(self, mock_logger, mock_authenticate):
        """Test listing files when authentication fails"""
        # Arrange
        mock_authenticate.return_value = None

        # Act
        result = GoogleDriveAPI.list_files()

        # Assert
        assert result == []
        mock_logger.error.assert_called_with("Failed to authenticate, aborting file listing.")

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.logger')
    @patch('google_api.google_drive_api.Config')
    def test_list_files_http_error(self, mock_config, mock_logger, mock_build, mock_authenticate):
        """Test listing files when HTTP error occurs"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_list = Mock()
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list

        http_error = HttpError(
            resp=Mock(status=403),
            content=b'Access denied'
        )
        mock_list.execute.side_effect = http_error

        # Act
        result = GoogleDriveAPI.list_files()

        # Assert
        assert result == []
        mock_logger.error.assert_called()

    @patch('google_api.google_drive_api.GoogleDriveAPI._authenticate')
    @patch('google_api.google_drive_api.build')
    @patch('google_api.google_drive_api.Config')
    def test_list_files_empty_folder(self, mock_config, mock_build, mock_authenticate):
        """Test listing files in an empty folder"""
        # Arrange
        mock_config.GD_PARENT_FOLDER_ID = 'parent-folder-id'

        mock_creds = Mock()
        mock_authenticate.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files = Mock()
        mock_list = Mock()
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list
        mock_list.execute.return_value = {'files': []}

        # Act
        result = GoogleDriveAPI.list_files()

        # Assert
        assert result == []


class TestGoogleDriveAPIConstants:
    """Test suite for GoogleDriveAPI constants"""

    def test_scopes_defined(self):
        """Test that SCOPES is properly defined"""
        assert GoogleDriveAPI.SCOPES == ["https://www.googleapis.com/auth/drive"]

    def test_parent_folder_id_exists(self):
        """Test that PARENT_FOLDER_ID is accessible"""
        # Just verify that the attribute exists
        assert hasattr(GoogleDriveAPI, 'PARENT_FOLDER_ID')
        assert GoogleDriveAPI.PARENT_FOLDER_ID is not None
