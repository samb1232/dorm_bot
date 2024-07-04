import logging
import config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


logger = logging.getLogger(__name__)


class GoogleDriveAPI:
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    CREDENTIALS_FILE = "google_drive_key.json"
    PARENT_FOLDER_ID = config.GD_PARENT_FOLDER_ID

    @staticmethod
    def _authenticate():
        try:
            credentials = service_account.Credentials.from_service_account_file(
                GoogleDriveAPI.CREDENTIALS_FILE,
                scopes=GoogleDriveAPI.SCOPES)
            return credentials
        except Exception as e:
            logger.error(f"Error authenticating: {e}")
            return None

    @staticmethod
    def upload_file(file_path, file_name):
        creds = GoogleDriveAPI._authenticate()
        if not creds:
            logger.error("Failed to authenticate, aborting upload.")
            return

        service = build("drive", "v3", credentials=creds)

        try:
            file_metadata = {
                'name': file_name,
                'parents': [GoogleDriveAPI.PARENT_FOLDER_ID]}

            # Specify the MIME type of the file
            media = MediaFileUpload(file_path, resumable=True)

            service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            logger.info(f"File {file_name} uploaded successfully")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
